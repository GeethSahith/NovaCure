from fastapi import APIRouter, Depends, HTTPException, status
from schemas.purchase import PoCreate, GenericResponse
from services.purchase import logic
from dependencies import get_current_user, require_warehouse

router = APIRouter(prefix="/purchase", tags=["Procurement"])

@router.post("/orders", response_model=GenericResponse)
async def create_po(req: PoCreate, current_user: dict = Depends(require_warehouse)):
    """Warehouse ONLY: Create a new PO to order goods from a vendor."""
    # Ensure they only order for their own branch (unless admin)
    if current_user["role"] == "warehouse_supervisor" and current_user.get("branch_code") != req.branch_code:
        raise HTTPException(status_code=403, detail="Can only create POs for your own branch.")
        
    try:
        data = logic.create_purchase_order(req.model_dump())
        return GenericResponse(success=True, data=data)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/orders", response_model=GenericResponse)
async def list_pos(current_user: dict = Depends(get_current_user)):
    """List POs based on role."""
    if current_user["role"] == "warehouse_supervisor":
        data = logic.get_branch_pos(current_user.get("branch_code", ""))
    else:
        # Admin or Manager
        data = logic.get_all_pos()
    return GenericResponse(success=True, data={"orders": data})

@router.put("/orders/{po_id}/receive", response_model=GenericResponse)
async def receive_po(po_id: str, current_user: dict = Depends(require_warehouse)):
    """Mark PO as received physically."""
    try:
        data = logic.mark_po_received(po_id)
        return GenericResponse(success=True, data=data)
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))
