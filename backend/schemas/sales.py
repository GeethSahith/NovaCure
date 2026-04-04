from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class SaleItemCreate(BaseModel):
    product_id: str
    batch_number: str
    quantity: int
    unit_price: float

class SaleCreate(BaseModel):
    branch_code: str
    customer_name: Optional[str] = "Walk-in Customer"
    payment_method: str = "cash"
    items: List[SaleItemCreate]

class GenericResponse(BaseModel):
    success: bool = True
    data: Optional[dict | list] = None
    error: Optional[str] = None
