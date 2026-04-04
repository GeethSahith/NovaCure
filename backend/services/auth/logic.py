"""
NovaCure — Auth Service Business Logic
Wraps Supabase Auth for signup/login and manages the 'profiles' table
that stores user_id → role mapping.
"""

from database import get_admin_client, get_anon_client
from dependencies import VALID_ROLES


# ═══════════════════════════════════════════════════════════
#  SIGN UP
# ═══════════════════════════════════════════════════════════

def signup_user(email: str, password: str, full_name: str, role: str, branch_code: str | None) -> dict:
    """
    1. Creates user in Supabase Auth
    2. Inserts a row in 'profiles' table with role + metadata
    Returns dict with user info + tokens.
    """
    if role not in VALID_ROLES:
        raise ValueError(f"Invalid role '{role}'. Must be one of: {VALID_ROLES}")

    # Step 1 — Create auth user via Supabase Auth (service-role)
    admin = get_admin_client()
    auth_response = admin.auth.admin.create_user({
        "email": email,
        "password": password,
        "email_confirm": True,            # auto-confirm for hackathon
        "user_metadata": {
            "full_name": full_name,
        },
    })

    user = auth_response.user
    if not user:
        raise Exception("Supabase Auth failed to create user")

    user_id = user.id

    # Step 2 — Insert profile row (service-role bypasses RLS)
    admin.table("profiles").insert({
        "id": user_id,
        "email": email,
        "full_name": full_name,
        "role": role,
        "branch_code": branch_code,
    }).execute()

    return {
        "user_id": user_id,
        "email": email,
        "full_name": full_name,
        "role": role,
        "branch_code": branch_code,
    }


# ═══════════════════════════════════════════════════════════
#  LOG IN
# ═══════════════════════════════════════════════════════════

def login_user(email: str, password: str) -> dict:
    """
    Authenticates via Supabase Auth → returns access_token + refresh_token.
    Also fetches the user's role from profiles.
    """
    anon = get_anon_client()
    auth_response = anon.auth.sign_in_with_password({
        "email": email,
        "password": password,
    })

    session = auth_response.session
    user = auth_response.user

    if not session or not user:
        raise Exception("Invalid email or password")

    user_id = user.id

    # Fetch role from profiles
    admin = get_admin_client()
    profile_res = (
        admin.table("profiles")
        .select("role, full_name, branch_code")
        .eq("id", user_id)
        .maybe_single()
        .execute()
    )

    profile = profile_res.data or {}

    return {
        "access_token": session.access_token,
        "refresh_token": session.refresh_token,
        "expires_at": session.expires_at,
        "user": {
            "user_id": user_id,
            "email": user.email,
            "full_name": profile.get("full_name", ""),
            "role": profile.get("role", "unknown"),
            "branch_code": profile.get("branch_code"),
        },
    }


# ═══════════════════════════════════════════════════════════
#  TOKEN REFRESH
# ═══════════════════════════════════════════════════════════

def refresh_session(refresh_token: str) -> dict:
    """Exchange a refresh token for a new access token."""
    anon = get_anon_client()
    auth_response = anon.auth.refresh_session(refresh_token)

    session = auth_response.session
    if not session:
        raise Exception("Failed to refresh token")

    return {
        "access_token": session.access_token,
        "refresh_token": session.refresh_token,
        "expires_at": session.expires_at,
    }


# ═══════════════════════════════════════════════════════════
#  GET PROFILE (me)
# ═══════════════════════════════════════════════════════════

def get_profile(user_id: str) -> dict | None:
    """Fetch full profile from profiles table."""
    admin = get_admin_client()
    res = (
        admin.table("profiles")
        .select("*")
        .eq("id", user_id)
        .maybe_single()
        .execute()
    )
    return res.data


# ═══════════════════════════════════════════════════════════
#  UPDATE ROLE  (admin only)
# ═══════════════════════════════════════════════════════════

def update_user_role(target_user_id: str, new_role: str) -> dict:
    """Update a user's role in the profiles table. Admin-only."""
    if new_role not in VALID_ROLES:
        raise ValueError(f"Invalid role '{new_role}'. Must be one of: {VALID_ROLES}")

    admin = get_admin_client()
    res = (
        admin.table("profiles")
        .update({"role": new_role})
        .eq("id", target_user_id)
        .execute()
    )

    if not res.data:
        raise Exception(f"User {target_user_id} not found")

    return {"user_id": target_user_id, "updated_role": new_role}


# ═══════════════════════════════════════════════════════════
#  LIST USERS  (admin only)
# ═══════════════════════════════════════════════════════════

def list_users() -> list[dict]:
    """Return all profiles. Admin-only."""
    admin = get_admin_client()
    res = admin.table("profiles").select("*").execute()
    return res.data or []


# ═══════════════════════════════════════════════════════════
#  LOG OUT
# ═══════════════════════════════════════════════════════════

def logout_user(token: str) -> None:
    """Sign out the user (invalidates the session on Supabase side)."""
    anon = get_anon_client()
    anon.auth.sign_out()
