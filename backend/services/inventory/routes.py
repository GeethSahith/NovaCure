from fastapi import APIRouter, Depends, HTTPException, status
from schemas.inventory import ProductCreate, InventoryAddRequest, ApiEnvelope
from services.inventory import logic
from dependencies import get_current_user, require_warehouse

router = APIRouter(prefix="/inventory", tags=["Inventory"])

@router.post("/products", response_model=ApiEnvelope)
async def create_product(req: ProductCreate, current_user: dict = Depends(require_warehouse)):
    """Admin/Warehouse strictly: Add a new product to the catalog."""
    try:
        data = logic.create_product(req.model_dump())
        return ApiEnvelope(success=True, data=data)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/products", response_model=ApiEnvelope)
async def list_products(current_user: dict = Depends(get_current_user)):
    """Anyone logged in can view the product catalog."""
    data = logic.list_products()
    return ApiEnvelope(success=True, data={"products": data})

@router.post("/stock", response_model=ApiEnvelope)
async def add_stock(req: InventoryAddRequest, current_user: dict = Depends(require_warehouse)):
    """Admin/Warehouse strictly: Add incoming stock manually for hackathon testing."""
    try:
        # Ensure we format the date correctly for Postgres
        payload = req.model_dump()
        payload["expiry_date"] = payload["expiry_date"].isoformat()
        
        data = logic.add_stock(payload)
        return ApiEnvelope(success=True, data=data)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/stock/{branch_code}", response_model=ApiEnvelope)
async def get_stock(branch_code: str, current_user: dict = Depends(get_current_user)):
    """View current stock levels for a specific branch."""
    data = logic.get_stock_levels(branch_code)
    return ApiEnvelope(success=True, data={"stock": data})
