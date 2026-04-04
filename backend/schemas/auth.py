"""
NovaCure — Auth Schemas (Pydantic request / response models)
"""

from pydantic import BaseModel, EmailStr
from typing import Optional


# ── Requests ──────────────────────────────────────────────

class SignUpRequest(BaseModel):
    email: EmailStr
    password: str
    full_name: str
    role: str = "pharmacist"
    branch_code: Optional[str] = None            


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenRefreshRequest(BaseModel):
    refresh_token: str


class RoleUpdateRequest(BaseModel):
    role: str                                     


class ProfileUpdateRequest(BaseModel):
    full_name: Optional[str] = None
    branch_id: Optional[str] = None

class AuthResponse(BaseModel):
    """Standard envelope for auth endpoints."""
    success: bool = True
    data: Optional[dict] = None
    error: Optional[str] = None


class UserProfile(BaseModel):
    id: str
    email: str
    full_name: Optional[str] = None
    role: str
    branch_id: Optional[str] = None
