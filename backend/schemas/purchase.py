from pydantic import BaseModel
from typing import List, Optional

class PoItem(BaseModel):
    product_id: str
    qty_ordered: int
    qty_received: int = 0

class PoCreate(BaseModel):
    vendor_name: str
    branch_code: str
    items: List[PoItem]

class GenericResponse(BaseModel):
    success: bool = True
    data: Optional[dict | list] = None
    error: Optional[str] = None
