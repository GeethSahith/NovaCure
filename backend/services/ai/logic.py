from database import get_admin_client

def log_ai_event(event_data: dict) -> dict:
    """Simulate generating an AI insight, anomaly flag, or forecast."""
    admin = get_admin_client()
    res = admin.table("ai_events").insert(event_data).execute()
    if not res.data:
        raise Exception("Failed to log AI event")
    return res.data[0]

def get_pending_events(branch_code: str = None) -> list[dict]:
    """Fetch all pending AI recommendations for human-in-the-loop review."""
    admin = get_admin_client()
    query = admin.table("ai_events").select("*").eq("status", "pending")
    if branch_code:
        query = query.eq("branch_code", branch_code)
        
    res = query.order("created_at", desc=True).execute()
    return res.data or []

def review_ai_event(event_id: str, new_status: str) -> dict:
    """Human-in-the-loop: Accept or dismiss the AI's recommendation."""
    admin = get_admin_client()
    res = admin.table("ai_events").update({"status": new_status}).eq("id", event_id).execute()
    if not res.data:
        raise Exception(f"AI Event {event_id} not found")
    return res.data[0]
