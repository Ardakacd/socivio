from typing import Optional
from pydantic import BaseModel, EmailStr, Field


# User Models
class UserBase(BaseModel):
    name: str
    email: EmailStr

class UserCreate(UserBase):
    user_id: str
    password: str = Field(..., min_length=6, description="Password must be at least 6 characters long")

class UserRegister(UserBase):
    password: str = Field(..., min_length=6, description="Password must be at least 6 characters long")

class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = Field(None, min_length=6, description="Password must be at least 6 characters long")

class User(UserBase):
    id: int  # Internal DB ID
    user_id: str  # Public-facing UUID for API
    password: Optional[str] = None
    created_at: Optional[str] = None

    class Config:
        from_attributes = True
        arbitrary_types_allowed = True


# Authentication Models
class UserLogin(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6, description="Password must be at least 6 characters long")

class PasswordChangeRequest(BaseModel):
    current_password: str = Field(..., min_length=6, description="Current password")
    new_password: str = Field(..., min_length=6, description="New password must be at least 6 characters long")

class Token(BaseModel):
    access_token: str
    refresh_token: str
    user_name: str
    
class TokenData(BaseModel):
    user_id: Optional[int] = None

class RefreshTokenRequest(BaseModel):
    refresh_token: str