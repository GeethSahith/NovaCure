from database import get_admin_client

def process_pos_sale(pharmacist_id: str, sale_data: dict) -> dict:
    admin = get_admin_client()
    branch_code = sale_data["branch_code"]
    items = sale_data["items"]
    
    total_amount = 0.0
    inventory_updates = []
    
    # 1. VERIFY STOCK
    for item in items:
        # Fetch the exact batch stock
        stock_req = (
            admin.table("inventory")
            .select("id, quantity")
            .eq("product_id", item["product_id"])
            .eq("branch_code", branch_code)
            .eq("batch_number", item["batch_number"])
            .maybe_single()
            .execute()
        )
        
        stock_row = stock_req.data
        if not stock_row:
            raise ValueError(f"Batch {item['batch_number']} not found for product {item['product_id']}")
        
        if stock_row["quantity"] < item["quantity"]:
            raise ValueError(f"Insufficient stock for batch {item['batch_number']}. Have {stock_row['quantity']}, requested {item['quantity']}")
            
        # Queue up the new deducted quantity
        new_qty = stock_row["quantity"] - item["quantity"]
        inventory_updates.append({"id": stock_row["id"], "new_qty": new_qty})
        
        # Calculate totals
        total_amount += (item["quantity"] * item["unit_price"])


    # 2. PERFORM DEDUCTIONS 
    # (Doing this sequentially in python for hackathon simplicity. If one fails mid-way, it's a partial deduction, 
    # but sufficient for a demonstration)
    for update in inventory_updates:
        admin.table("inventory").update({"quantity": update["new_qty"]}).eq("id", update["id"]).execute()


    # 3. CREATE SALE RECORD (7-table schema approach)
    sale_record = {
        "branch_code": branch_code,
        "pharmacist_id": pharmacist_id,
        "customer_name": sale_data["customer_name"],
        "total_amount": total_amount,
        "payment_status": "paid",
        "payment_method": sale_data["payment_method"],
        "items": items  # Array of dictionaries saved natively as JSONB
    }
    
    sale_req = admin.table("sales").insert(sale_record).execute()
    if not sale_req.data:
        raise Exception("Failed to write sale record")
        
    return sale_req.data[0]

def get_branch_sales(branch_code: str) -> list[dict]:
    admin = get_admin_client()
    res = admin.table("sales").select("*").eq("branch_code", branch_code).order("created_at", desc=True).execute()
    return res.data or []

def get_all_sales() -> list[dict]:
    admin = get_admin_client()
    res = admin.table("sales").select("*").order("created_at", desc=True).execute()
    return res.data or []
