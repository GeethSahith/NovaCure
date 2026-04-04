"""
NovaCure Platform — Supabase Client Factory
Two clients:
  • anon_client   — uses ANON key, passes user JWT → RLS enforced
  • admin_client  — uses SERVICE_ROLE key → bypasses RLS (admin-only server tasks)
"""

from supabase import create_client, Client
import config


def get_anon_client() -> Client:
    """Client that respects RLS.  Pair with user JWT via .auth.set_session()."""
    return create_client(config.SUPABASE_URL, config.SUPABASE_ANON_KEY)


def get_admin_client() -> Client:
    """Service-role client — bypasses RLS. Use only for admin server tasks."""
    return create_client(config.SUPABASE_URL, config.SUPABASE_SERVICE_ROLE_KEY)
