from typing import Any
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, Body
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session, select
import uuid

from app.db import get_session
from app.models.auth import (
    User, UserCreate, UserRead, UserUpdate, 
    Token, RefreshToken, OAuthAccount
)
from app.services.auth_service import auth_service
from app.dependencies import get_current_user, get_current_active_user
from app.config import settings

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/register", response_model=UserRead)
def register(user_in: UserCreate, session: Session = Depends(get_session)) -> Any:
    """
    Create new user.
    """
    user = session.exec(select(User).where(User.email == user_in.email)).first()
    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this email already exists in the system",
        )
    
    user_obj = User(
        email=user_in.email,
        username=user_in.username,
        hashed_password=auth_service.get_password_hash(user_in.password),
        full_name=user_in.username # Default full name to username
    )
    session.add(user_obj)
    session.commit()
    session.refresh(user_obj)
    return user_obj


@router.post("/login", response_model=Token)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: Session = Depends(get_session)
) -> Any:
    """
    OAuth2 compatible token login, get an access token for future requests.
    """
    user = session.exec(select(User).where(User.email == form_data.username)).first()
    if not user or not user.hashed_password:
        # OAuth users might not have a password
        raise HTTPException(status_code=400, detail="Incorrect email or password")
        
    if not auth_service.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect email or password")
        
    access_token = auth_service.create_access_token(user.id)
    refresh_token = auth_service.create_refresh_token(user.id, session, str(user.id))
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    }


@router.post("/refresh", response_model=Token)
def refresh_token(
    refresh_token: str = Body(..., embed=True),
    session: Session = Depends(get_session)
) -> Any:
    """
    Get new access token using refresh token with secure validation.

    Security features:
    - Validates JWT signature and expiration
    - Checks database for token revocation
    - Implements refresh token rotation (old token invalidated)

    Request body:
    {
        "refresh_token": "your_refresh_token_here"
    }
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired refresh token",
        headers={"WWW-Authenticate": "Bearer"},
    )

    # Verify refresh token with database revocation checking
    payload = auth_service.verify_refresh_token(refresh_token, session, credentials_exception)
    user_id = payload.sub

    # Verify user still exists and is active
    user = session.get(User, user_id)
    if not user or not user.is_active:
        raise credentials_exception

    # Revoke the old refresh token (rotation)
    auth_service.revoke_refresh_token(refresh_token, session)

    # Issue new tokens
    new_access_token = auth_service.create_access_token(user_id)
    new_refresh_token = auth_service.create_refresh_token(user_id, session, user_id)

    return {
        "access_token": new_access_token,
        "refresh_token": new_refresh_token,
        "token_type": "bearer",
        "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    }


@router.get("/me", response_model=UserRead)
def read_users_me(
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    Get current user.
    """
    return current_user


@router.post("/logout")
def logout(
    refresh_token: str = Body(..., embed=True),
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Logout user by revoking the provided refresh token.

    Security note: Access tokens cannot be revoked (they expire naturally).
    This endpoint revokes the refresh token to prevent obtaining new access tokens.

    Request body:
    {
        "refresh_token": "your_refresh_token_here"
    }
    """
    revoked = auth_service.revoke_refresh_token(refresh_token, session)

    return {
        "message": "Logged out successfully" if revoked else "Token already invalid",
        "revoked": revoked
    }


@router.post("/logout-all")
def logout_all(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Logout from all devices by revoking all refresh tokens for the current user.

    Useful for security events like password changes or suspected account compromise.
    """
    count = auth_service.revoke_all_user_tokens(str(current_user.id), session)

    return {
        "message": f"Revoked {count} refresh token(s)",
        "count": count
    }


@router.get("/oauth/{provider}")
def oauth_login(provider: str):
    """
    Initiate OAuth login.
    """
    if provider == "google":
        return {
            "url": f"https://accounts.google.com/o/oauth2/v2/auth?response_type=code&client_id={settings.GOOGLE_CLIENT_ID}&redirect_uri={settings.OAUTH_REDIRECT_BASE}/auth/callback/google&scope=openid%20email%20profile"
        }
    elif provider == "github":
        return {
            "url": f"https://github.com/login/oauth/authorize?client_id={settings.GITHUB_CLIENT_ID}&redirect_uri={settings.OAUTH_REDIRECT_BASE}/auth/callback/github&scope=user:email"
        }
    else:
        raise HTTPException(status_code=400, detail="Unsupported provider")


@router.post("/oauth/callback/{provider}", response_model=Token)
async def oauth_callback(
    provider: str,
    code: str,
    session: Session = Depends(get_session)
) -> Any:
    """
    OAuth callback - exchange code for tokens with secure account linking.

    Security features:
    - Links OAuth accounts to prevent account takeover
    - Verifies OAuth account ownership via provider ID
    - Trusted providers (Google/GitHub) auto-verify email addresses
    """
    # Get user info and OAuth credentials from provider
    if provider == "google":
        user_info = await auth_service.get_google_user(code)
        email = user_info.get("email")
        oauth_id = user_info.get("id") or user_info.get("sub")
        full_name = user_info.get("name")
        avatar_url = user_info.get("picture")

    elif provider == "github":
        user_info = await auth_service.get_github_user(code)
        email = user_info.get("email")
        oauth_id = str(user_info.get("id"))
        full_name = user_info.get("name")
        avatar_url = user_info.get("avatar_url")
    else:
        raise HTTPException(status_code=400, detail="Unsupported provider")

    if not email:
        raise HTTPException(status_code=400, detail="Could not retrieve email from provider")

    if not oauth_id:
        raise HTTPException(status_code=400, detail="Could not retrieve provider user ID")

    # Step 1: Check if this OAuth account already exists
    oauth_account = session.exec(
        select(OAuthAccount).where(
            OAuthAccount.oauth_name == provider,
            OAuthAccount.oauth_id == oauth_id
        )
    ).first()

    if oauth_account:
        # OAuth account exists - use the linked user
        user = session.get(User, oauth_account.user_id)
        if not user:
            raise HTTPException(status_code=500, detail="Linked user not found")

        # Update OAuth account info (access token may have changed)
        oauth_account.oauth_email = email
        oauth_account.account_email = email
        session.add(oauth_account)
        session.commit()

    else:
        # OAuth account doesn't exist - need to link or create

        # Step 2: Check if user with this email exists
        user = session.exec(select(User).where(User.email == email)).first()

        if user:
            # User exists - link OAuth account
            # For trusted providers (Google/GitHub), we trust the email verification
            # and allow linking to existing account
            pass  # User already found, will create OAuth link below
        else:
            # Step 3: Create new user
            # Generate unique username from email
            base_username = email.split("@")[0]
            username = base_username
            counter = 1
            while session.exec(select(User).where(User.username == username)).first():
                username = f"{base_username}{counter}"
                counter += 1

            user = User(
                email=email,
                username=username,
                full_name=full_name or username,
                is_active=True,
                is_verified=True,  # OAuth emails are verified by provider
                avatar_url=avatar_url
            )
            session.add(user)
            session.commit()
            session.refresh(user)

        # Step 4: Create OAuth account link
        oauth_account = OAuthAccount(
            oauth_name=provider,
            oauth_id=oauth_id,
            oauth_email=email,
            account_id=oauth_id,  # Provider's user ID
            account_email=email,
            access_token="",  # Not storing provider tokens for now
            user_id=user.id
        )
        session.add(oauth_account)
        session.commit()

    # Update last login
    user.last_login = datetime.utcnow()
    session.add(user)
    session.commit()

    # Create application tokens
    access_token = auth_service.create_access_token(user.id)
    refresh_token = auth_service.create_refresh_token(user.id, session, str(user.id))

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    }


@router.put("/me", response_model=UserRead)
def update_user_profile(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_active_user),
    session: Session = Depends(get_session)
) -> Any:
    """
    Update current user's profile.

    Allows updating:
    - email
    - username
    - full_name
    - password
    """
    import logging
    logger = logging.getLogger(__name__)
    logger.info(f"Update request: {user_update.model_dump()}")
    # Check if email is being changed and if it's already taken
    if user_update.email and user_update.email != current_user.email:
        existing_user = session.exec(
            select(User).where(User.email == user_update.email)
        ).first()
        if existing_user:
            raise HTTPException(
                status_code=400,
                detail="Email already registered"
            )
        current_user.email = user_update.email

    # Check if username is being changed and if it's already taken
    if user_update.username and user_update.username != current_user.username:
        existing_user = session.exec(
            select(User).where(User.username == user_update.username)
        ).first()
        if existing_user:
            raise HTTPException(
                status_code=400,
                detail="Username already taken"
            )
        current_user.username = user_update.username

    # Update full name
    if user_update.full_name is not None:
        current_user.full_name = user_update.full_name

    # Update password if provided
    if user_update.password:
        current_user.hashed_password = auth_service.get_password_hash(user_update.password)
        # Revoke all refresh tokens on password change for security
        auth_service.revoke_all_user_tokens(current_user.id, session)

    session.add(current_user)
    session.commit()
    session.refresh(current_user)

    return current_user


@router.delete("/me")
def delete_user_account(
    current_user: User = Depends(get_current_active_user),
    session: Session = Depends(get_session)
) -> Any:
    """
    Delete current user's account.

    This is a permanent action that:
    - Deletes all user's refresh tokens
    - Deletes all user's OAuth accounts
    - Deletes the user account
    - Note: Transcripts are preserved due to composite primary key
    """
    # Delete all refresh tokens
    tokens = session.exec(
        select(RefreshToken).where(RefreshToken.user_id == current_user.id)
    ).all()
    for token in tokens:
        session.delete(token)

    # Delete all OAuth accounts
    oauth_accounts = session.exec(
        select(OAuthAccount).where(OAuthAccount.user_id == current_user.id)
    ).all()
    for oauth_account in oauth_accounts:
        session.delete(oauth_account)

    # Delete the user
    session.delete(current_user)
    session.commit()

    return {"message": "Account deleted successfully"}
