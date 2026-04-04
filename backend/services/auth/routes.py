"""
NovaCure — Auth Service Routes
Endpoints: signup, login, logout, refresh, me, update role, list users
"""

from fastapi import APIRouter, Depends, HTTPException, status

from schemas.auth import (
    SignUpRequest,
    LoginRequest,
    TokenRefreshRequest,
    RoleUpdateRequest,
    AuthResponse,
)
from services.auth import logic
from dependencies import get_current_user, require_admin

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/signup", response_model=AuthResponse)
async def signup(req: SignUpRequest):
    """Register a new user. Creates Supabase Auth user + profiles row."""
    try:
        data = logic.signup_user(
            email=req.email,
            password=req.password,
            full_name=req.full_name,
            role=req.role,
            branch_code=req.branch_code,
        )
        return AuthResponse(success=True, data=data)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.post("/login", response_model=AuthResponse)
async def login(req: LoginRequest):
    try:
        data = logic.login_user(email=req.email, password=req.password)
        return AuthResponse(success=True, data=data)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))

@router.post("/logout", response_model=AuthResponse)
async def logout(current_user: dict = Depends(get_current_user)):
    try:
        logic.logout_user(current_user["token"])
        return AuthResponse(success=True, data={"message": "Logged out"})
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.post("/refresh", response_model=AuthResponse)
async def refresh(req: TokenRefreshRequest):
    try:
        data = logic.refresh_session(req.refresh_token)
        return AuthResponse(success=True, data=data)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))

@router.get("/me", response_model=AuthResponse)
async def me(current_user: dict = Depends(get_current_user)):
    profile = logic.get_profile(current_user["user_id"])
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    return AuthResponse(success=True, data=profile)

@router.put("/users/{user_id}/role", response_model=AuthResponse)
async def update_role(
    user_id: str,
    req: RoleUpdateRequest,
    current_user: dict = Depends(require_admin),
):
    try:
        data = logic.update_user_role(target_user_id=user_id, new_role=req.role)
        return AuthResponse(success=True, data=data)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

@router.get("/users", response_model=AuthResponse)
async def list_users(current_user: dict = Depends(require_admin)):
    data = logic.list_users()
    return AuthResponse(success=True, data={"users": data})
