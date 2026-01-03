import uuid
from datetime import datetime
from typing import Optional, List
from sqlmodel import Field, Relationship, SQLModel
from pydantic import EmailStr


# Shared Properties
class UserBase(SQLModel):
    email: EmailStr = Field(unique=True, index=True, sa_column_kwargs={"unique": True})
    username: Optional[str] = Field(default=None, unique=True, index=True)
    is_active: bool = True
    is_verified: bool = False
    full_name: Optional[str] = None
    avatar_url: Optional[str] = None


# Database Models
class User(UserBase, table=True):
    __tablename__ = "users"

    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True, max_length=36)
    hashed_password: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_login: Optional[datetime] = None

    # Relationships
    oauth_accounts: List["OAuthAccount"] = Relationship(back_populates="user")
    refresh_tokens: List["RefreshToken"] = Relationship(back_populates="user")
    # transcripts: List["Transcript"] = Relationship(back_populates="user") # To be added later


class OAuthAccount(SQLModel, table=True):
    __tablename__ = "oauth_accounts"

    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True, max_length=36)
    oauth_name: str  # e.g. "google", "github"
    oauth_id: str    # The provider's user ID
    oauth_email: Optional[str] = None
    access_token: str
    expires_at: Optional[int] = None
    refresh_token: Optional[str] = None
    account_id: str
    account_email: str

    user_id: str = Field(foreign_key="users.id", max_length=36)
    user: User = Relationship(back_populates="oauth_accounts")
    
    # Composite index for oauth_name + oauth_id would be good, 
    # but SQLModel requires SA args for that.
    # We can handle uniqueness in logic or add SA args.


class RefreshToken(SQLModel, table=True):
    __tablename__ = "refresh_tokens"

    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True, max_length=36)
    token_hash: str = Field(index=True)
    expires_at: datetime
    created_at: datetime = Field(default_factory=datetime.utcnow)
    revoked: bool = False

    user_id: str = Field(foreign_key="users.id", max_length=36)
    user: User = Relationship(back_populates="refresh_tokens")


# Pydantic Schemas for API
class UserCreate(UserBase):
    password: str

class UserLogin(SQLModel):
    email: EmailStr
    password: str

class UserUpdate(SQLModel):
    email: Optional[EmailStr] = None
    username: Optional[str] = None
    full_name: Optional[str] = None
    password: Optional[str] = None

class UserRead(UserBase):
    id: str
    pass

class Token(SQLModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int

class TokenPayload(SQLModel):
    sub: str
    exp: int
    iat: int
    type: str
