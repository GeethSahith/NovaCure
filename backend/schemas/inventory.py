from pydantic import BaseModel
from typing import Optional, List
from datetime import date, datetime


# ── Products ──────────────────────────────────────────────

class ProductCreate(BaseModel):
    name: str
    category: Optional[str] = None
    reorder_threshold: int = 10
    is_controlled: bool = False

class ProductResponse(BaseModel):
    id: str
    name: str
    category: Optional[str] = None
    reorder_threshold: int
    is_controlled: bool
    created_at: datetime


# ── Inventory (Stock) ─────────────────────────────────────

class InventoryAddRequest(BaseModel):
    product_id: str
    branch_code: str
    batch_number: str
    expiry_date: date
    quantity: int
    unit_cost: float = 0.0

class InventoryResponse(BaseModel):
    id: str
    product_id: str
    branch_code: str
    batch_number: str
    expiry_date: date
    quantity: int
    unit_cost: float
    created_at: datetime


# ── Generic Response ──────────────────────────────────────

class ApiEnvelope(BaseModel):
    success: bool = True
    data: Optional[dict | list] = None
    error: Optional[str] = None
