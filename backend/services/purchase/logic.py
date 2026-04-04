from database import get_admin_client

def create_purchase_order(po_data: dict) -> dict:
    """Create a draft purchase order for a vendor, and automatically raise an Alert."""
    admin = get_admin_client()
    res = admin.table("purchase_orders").insert(po_data).execute()
    if not res.data:
        raise Exception("Failed to create PO")
        
    # AUTOMATION: Trigger a system alert so Admins see the PO was created
    alert_payload = {
        "event_type": "alert",
        "branch_code": po_data["branch_code"],
        "status": "pending",
        "data": {
            "message": f"New Purchase Order created for Vendor: {po_data['vendor_name']} at {po_data['branch_code']}",
            "po_id": res.data[0]['id']
        }
    }
    admin.table("ai_events").insert(alert_payload).execute()
    
    return res.data[0]

def get_active_vendors() -> list[dict]:
    """Fetch admins and warehouse supervisors to act as internal Vendors."""
    admin = get_admin_client()
    res = (
        admin.table("profiles")
        .select("id, full_name, role, branch_code")
        .in_("role", ["admin", "warehouse_supervisor"])
        .execute()
    )
    return res.data or []

def get_branch_pos(branch_code: str) -> list[dict]:
    """Get POs for a specific branch."""
    admin = get_admin_client()
    res = admin.table("purchase_orders").select("*").eq("branch_code", branch_code).order("created_at", desc=True).execute()
    return res.data or []

def get_all_pos() -> list[dict]:
    """Get all POs company-wide (Admin/Manager)."""
    admin = get_admin_client()
    res = admin.table("purchase_orders").select("*").order("created_at", desc=True).execute()
    return res.data or []

def mark_po_received(po_id: str) -> dict:
    """Mark PO as received. (In a full app, this would also add stock gracefully)."""
    admin = get_admin_client()
    res = admin.table("purchase_orders").update({"status": "received"}).eq("id", po_id).execute()
    if not res.data:
        raise Exception(f"PO {po_id} not found")
    return res.data[0]
