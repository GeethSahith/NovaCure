from pydantic import BaseModel
from typing import Optional, List

class BranchRevenue(BaseModel):
    branch_code: str
    total_revenue: float

class ExpiryRiskItem(BaseModel):
    product_name: str
    branch_code: str
    quantity_at_risk: int
    expiry_date: str

class AnalyticsResponse(BaseModel):
    revenue_data: List[BranchRevenue]
    expiry_risk: List[ExpiryRiskItem]
    
class GenericResponse(BaseModel):
    success: bool = True
    data: Optional[AnalyticsResponse] = None
    error: Optional[str] = None
