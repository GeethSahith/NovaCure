from database import get_admin_client
from datetime import datetime, timedelta

def get_revenue_analytics() -> list[dict]:
    """Calculate total revenue grouped loosely by branch."""
    admin = get_admin_client()
    # Fetch all sales. In production, you would do the math inside a SQL GROUP BY via RPC.
    res = admin.table("sales").select("branch_code, total_amount").execute()
    sales = res.data or []
    
    aggregation = {}
    for sale in sales:
        branch = sale.get("branch_code", "Unknown")
        amt = float(sale.get("total_amount", 0))
        aggregation[branch] = aggregation.get(branch, 0) + amt
        
    # Formatting for API response
    result = [{"branch_code": k, "total_revenue": v} for k, v in aggregation.items()]
    return result

def get_expiry_risk() -> list[dict]:
    """Find inventory expiring in the next 90 days. Simulating a basic BI query."""
    admin = get_admin_client()
    ninety_days_from_now = (datetime.now() + timedelta(days=90)).strftime("%Y-%m-%d")
    
    res = (
        admin.table("inventory")
        .select("quantity, expiry_date, branch_code, products(name)")
        .lte("expiry_date", ninety_days_from_now)
        .gt("quantity", 0)
        .execute()
    )
    
    risk_items = []
    for item in (res.data or []):
        risk_items.append({
            "product_name": item["products"]["name"] if item.get("products") else "Unknown",
            "branch_code": item["branch_code"],
            "quantity_at_risk": item["quantity"],
            "expiry_date": str(item["expiry_date"])
        })
        
    return risk_items
