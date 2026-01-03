from datetime import datetime, timedelta
from typing import Optional, Union, Dict, Any
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlmodel import Session, select
import httpx

from app.config import settings
from app.models.auth import User, RefreshToken, TokenPayload

# Password Context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class AuthService:
    def _truncate_password(self, password: str) -> str:
        """Truncate password to 72 bytes for bcrypt, preserving UTF-8 encoding"""
        encoded = password.encode('utf-8')
        if len(encoded) <= 72:
            return password
        # Truncate and decode, ensuring we don't break multi-byte characters
        truncated = encoded[:72]
        # Find the last valid UTF-8 character boundary
        while len(truncated) > 0:
            try:
                return truncated.decode('utf-8')
            except UnicodeDecodeError:
                truncated = truncated[:-1]
        return password[:50]  # Fallback to ASCII-safe truncation

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return pwd_context.verify(self._truncate_password(plain_password), hashed_password)

    def get_password_hash(self, password: str) -> str:
        return pwd_context.hash(self._truncate_password(password))

    def create_access_token(self, subject: Union[str, Any], expires_delta: Optional[timedelta] = None) -> str:
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        
        to_encode = {
            "sub": str(subject), 
            "exp": expire,
            "type": "access",
            "iat": datetime.utcnow()
        }
        encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
        return encoded_jwt

    def create_refresh_token(self, subject: Union[str, Any], session: Session, user_id: str) -> str:
        """
        Create a new refresh token with secure hashing and database tracking.

        Security measures:
        - JWT signed with server secret
        - SHA256 hash stored in database for revocation checking
        - Refresh token rotation: new token issued on each refresh
        """
        import hashlib

        expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)

        to_encode = {
            "sub": str(subject),
            "exp": expire,
            "type": "refresh",
            "iat": datetime.utcnow()
        }
        encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)

        # Store SHA256 hash of the token for revocation checking
        # This prevents token reuse if database is compromised
        token_hash = hashlib.sha256(encoded_jwt.encode()).hexdigest()

        db_token = RefreshToken(
            token_hash=token_hash,
            expires_at=expire,
            user_id=user_id,
            revoked=False
        )

        session.add(db_token)
        session.commit()
        session.refresh(db_token)

        return encoded_jwt

    def verify_token(self, token: str, credential_exception) -> TokenPayload:
        """Verify JWT token signature and expiration (does NOT check database for revocation)"""
        try:
            payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
            token_data = TokenPayload(**payload)
            return token_data
        except JWTError:
            raise credential_exception

    def verify_refresh_token(self, token: str, session: Session, credential_exception) -> TokenPayload:
        """
        Verify refresh token with database revocation checking.

        Security checks:
        1. JWT signature and expiration validation
        2. Token type must be "refresh"
        3. Token hash must exist in database
        4. Token must not be revoked
        5. Token must not be expired in database

        Returns TokenPayload if all checks pass, raises credential_exception otherwise.
        """
        import hashlib

        # Step 1: Verify JWT signature and expiration
        try:
            payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
            token_data = TokenPayload(**payload)
        except JWTError:
            raise credential_exception

        # Step 2: Verify token type
        if token_data.type != "refresh":
            raise credential_exception

        # Step 3 & 4 & 5: Check database for revocation and validity
        token_hash = hashlib.sha256(token.encode()).hexdigest()
        db_token = session.exec(
            select(RefreshToken).where(RefreshToken.token_hash == token_hash)
        ).first()

        if not db_token:
            # Token hash not found in database
            raise credential_exception

        if db_token.revoked:
            # Token has been revoked
            raise credential_exception

        if db_token.expires_at < datetime.utcnow():
            # Token expired in database (belt-and-suspenders with JWT exp)
            raise credential_exception

        return token_data

    def revoke_refresh_token(self, token: str, session: Session) -> bool:
        """
        Revoke a refresh token by marking it as revoked in the database.

        Returns True if token was found and revoked, False otherwise.
        """
        import hashlib

        token_hash = hashlib.sha256(token.encode()).hexdigest()
        db_token = session.exec(
            select(RefreshToken).where(RefreshToken.token_hash == token_hash)
        ).first()

        if db_token:
            db_token.revoked = True
            session.add(db_token)
            session.commit()
            return True

        return False

    def revoke_all_user_tokens(self, user_id: str, session: Session) -> int:
        """
        Revoke all refresh tokens for a user (e.g., on password change or security event).

        Returns the number of tokens revoked.
        """
        tokens = session.exec(
            select(RefreshToken).where(
                RefreshToken.user_id == user_id,
                RefreshToken.revoked == False
            )
        ).all()

        count = 0
        for token in tokens:
            token.revoked = True
            session.add(token)
            count += 1

        if count > 0:
            session.commit()

        return count
    
    async def get_google_user(self, code: str) -> Dict[str, Any]:
        """Exchange code for Google user info"""
        async with httpx.AsyncClient() as client:
            # 1. Exchange code for token
            token_url = "https://oauth2.googleapis.com/token"
            data = {
                "code": code,
                "client_id": settings.GOOGLE_CLIENT_ID,
                "client_secret": settings.GOOGLE_CLIENT_SECRET,
                "redirect_uri": f"{settings.OAUTH_REDIRECT_BASE}/auth/callback/google",
                "grant_type": "authorization_code"
            }
            response = await client.post(token_url, data=data)
            response.raise_for_status()
            token_data = response.json()
            access_token = token_data["access_token"]
            
            # 2. Get user info
            user_info_url = "https://www.googleapis.com/oauth2/v2/userinfo"
            headers = {"Authorization": f"Bearer {access_token}"}
            user_response = await client.get(user_info_url, headers=headers)
            user_response.raise_for_status()
            return user_response.json()

    async def get_github_user(self, code: str) -> Dict[str, Any]:
        """Exchange code for GitHub user info"""
        async with httpx.AsyncClient() as client:
            # 1. Exchange code for token
            token_url = "https://github.com/login/oauth/access_token"
            data = {
                "client_id": settings.GITHUB_CLIENT_ID,
                "client_secret": settings.GITHUB_CLIENT_SECRET,
                "code": code,
                "redirect_uri": f"{settings.OAUTH_REDIRECT_BASE}/auth/callback/github"
            }
            headers = {"Accept": "application/json"}
            response = await client.post(token_url, json=data, headers=headers)
            response.raise_for_status()
            token_data = response.json()
            
            if "error" in token_data:
                raise Exception(token_data.get("error_description", "Unknown GitHub error"))
                
            access_token = token_data["access_token"]
            
            # 2. Get user info
            user_info_url = "https://api.github.com/user"
            headers = {
                "Authorization": f"Bearer {access_token}",
                "Accept": "application/json"
            }
            user_response = await client.get(user_info_url, headers=headers)
            user_response.raise_for_status()
            user_data = user_response.json()
            
            # GitHub doesn't always return email in public profile
            if not user_data.get("email"):
                emails_url = "https://api.github.com/user/emails"
                emails_resp = await client.get(emails_url, headers=headers)
                if emails_resp.status_code == 200:
                    emails = emails_resp.json()
                    primary_email = next((e for e in emails if e["primary"]), None)
                    if primary_email:
                        user_data["email"] = primary_email["email"]
            
            return user_data

auth_service = AuthService()
