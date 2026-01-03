from typing import Generator, Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from sqlmodel import Session, select
import uuid

from app.db import get_session
from app.models.auth import User, TokenPayload
from app.services.auth_service import auth_service
from app.config import settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login")

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    session: Session = Depends(get_session)
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    token_data = auth_service.verify_token(token, credentials_exception)
    if token_data.type != "access":
        raise credentials_exception

    user = session.get(User, token_data.sub)
    if user is None:
        raise credentials_exception

    return user

async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

async def get_current_user_optional(
    token: Optional[str] = Depends(oauth2_scheme), # This will enforce token existence if not optional in OAuth2PasswordBearer... 
    # Actually OAuth2PasswordBearer(auto_error=False) creates optional.
    # We should define a separate scheme or just handle the error.
    session: Session = Depends(get_session)
) -> Optional[User]:
    # TODO: Implement optional auth logic if needed (e.g. for guest viewing if allowed)
    # For now, just a placeholder.
    return None
