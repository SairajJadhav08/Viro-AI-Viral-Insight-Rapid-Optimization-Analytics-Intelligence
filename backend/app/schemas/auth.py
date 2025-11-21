"""
Authentication Pydantic schemas
"""
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime


class SignUpRequest(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    password: str
    phone: Optional[str] = None
    role: Optional[str] = "user"
    
    class Config:
        # Allow extra fields for camelCase compatibility
        extra = "allow"


class SignInRequest(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: int
    email: str
    first_name: str
    last_name: str
    phone: Optional[str]
    role: Optional[str]
    qualification: Optional[str]
    occupation: Optional[str]
    professional_summary: Optional[str]
    skills: Optional[list]
    experience: Optional[list]
    publications: Optional[list]
    awards: Optional[list]
    social_links: Optional[dict]
    avatar_url: Optional[str]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class AuthResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


class UserUpdateRequest(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    qualification: Optional[str] = None
    occupation: Optional[str] = None
    professional_summary: Optional[str] = None
    skills: Optional[list] = None
    experience: Optional[list] = None
    publications: Optional[list] = None
    awards: Optional[list] = None
    social_links: Optional[dict] = None
    avatar_url: Optional[str] = None

