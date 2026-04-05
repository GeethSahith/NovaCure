"""
NovaCure Platform — Configuration
Loads all settings from .env file.
"""

import os
from dotenv import load_dotenv

load_dotenv(override=True)

# ── Supabase ──────────────────────────────────────────────
SUPABASE_URL: str = os.getenv("SUPABASE_URL", "")
SUPABASE_ANON_KEY: str = os.getenv("SUPABASE_ANON_KEY", "")
SUPABASE_SERVICE_ROLE_KEY: str = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "")

# ── JWT ───────────────────────────────────────────────────
# Supabase signs JWTs with its own JWT secret.
# You find this in Supabase Dashboard → Settings → API → JWT Secret.
SUPABASE_JWT_SECRET: str = os.getenv("SUPABASE_JWT_SECRET", "")
JWT_ALGORITHM: str = "HS256"

# ── App ───────────────────────────────────────────────────
APP_NAME: str = "NovaCure Platform"
DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"
