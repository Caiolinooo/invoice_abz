"""
Authentication models
"""
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime


class LoginRequest(BaseModel):
    """Login request model"""
    email: EmailStr
    password: str


class User(BaseModel):
    """User model from Supabase"""
    id: str
    email: str
    name: str
    role: str
    is_active: bool
    created_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class Token(BaseModel):
    """JWT token response"""
    access_token: str
    token_type: str = "bearer"
    expires_in: int  # seconds
    user: User


class TokenData(BaseModel):
    """JWT token payload data"""
    user_id: str
    email: str
    role: str
    exp: int
    iat: int
    jti: str  # JWT ID for token revocation


class AuditLogCreate(BaseModel):
    """Audit log creation model"""
    user_id: Optional[str] = None
    action: str
    ip_address: str
    user_agent: str
    success: bool
    details: Optional[str] = None

