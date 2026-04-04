from fastapi import APIRouter, Depends, HTTPException, status
from schemas.sales import SaleCreate, GenericResponse
from services.sales import logic
from dependencies import get_current_user, require_pharmacist

router = APIRouter(prefix="/sales", tags=["Sales"])

@router.post("/orders", response_model=GenericResponse)
async def create_sale(req: SaleCreate, current_user: dict = Depends(require_pharmacist)):
    """Pharmacist ONLY: Process a complete sale, deducts stock."""
    # Security: ensure pharmacist is only selling from their assigned branch!
    if current_user["role"] == "pharmacist" and current_user.get("branch_code") != req.branch_code:
         raise HTTPException(status_code=403, detail="Pharmacists can only create sales for their assigned branch.")
         
    try:
        data = logic.process_pos_sale(current_user["user_id"], req.model_dump())
        return GenericResponse(success=True, data=data)
    except ValueError as e:
        # Valuation error like insufficient stock
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"System Error: {str(e)}")

@router.get("/orders", response_model=GenericResponse)
async def list_sales(current_user: dict = Depends(get_current_user)):
    """
    Get sales based on role. 
    Pharmacist -> views own branch.
    Admin/Regional Manager -> views all.
    """
    if current_user["role"] == "pharmacist":
        data = logic.get_branch_sales(current_user.get("branch_code", ""))
    else:
        # Admin or Regional Manager sees across the entire company
        data = logic.get_all_sales()
        
    return GenericResponse(success=True, data={"sales": data})
