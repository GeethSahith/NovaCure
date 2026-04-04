from database import get_admin_client

def create_product(product_data: dict) -> dict:
    """Insert a new product into the catalog."""
    admin = get_admin_client()
    res = admin.table("products").insert(product_data).execute()
    if not res.data:
        raise Exception("Failed to create product")
    return res.data[0]

def list_products() -> list[dict]:
    """Get all products."""
    admin = get_admin_client()
    res = admin.table("products").select("*").execute()
    return res.data or []

def add_stock(stock_data: dict) -> dict:
    """
    Adds stock to inventory. If the exact product + branch + batch exists, 
    we need to increment its quantity. Otherwise, create a new row.
    """
    admin = get_admin_client()
    
    # Check if this exact batch exists
    check = (
        admin.table("inventory")
        .select("*")
        .eq("product_id", stock_data["product_id"])
        .eq("branch_code", stock_data["branch_code"])
        .eq("batch_number", stock_data["batch_number"])
        .maybe_single()
        .execute()
    )
    
    if check.data:
        # Increment existing stock
        new_qty = check.data["quantity"] + stock_data["quantity"]
        res = (
            admin.table("inventory")
            .update({"quantity": new_qty})
            .eq("id", check.data["id"])
            .execute()
        )
    else:
        # Insert new stock
        res = admin.table("inventory").insert(stock_data).execute()
        
    if not res.data:
        raise Exception("Failed to add stock")
    return res.data[0]

def get_stock_levels(branch_code: str) -> list[dict]:
    """Get all available inventory for a specific branch."""
    admin = get_admin_client()
    res = (
        admin.table("inventory")
        .select("*, products(name, category)")
        .eq("branch_code", branch_code)
        .gt("quantity", 0) # Only show stock > 0
        .execute()
    )
    return res.data or []
