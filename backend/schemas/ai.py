from pydantic import BaseModel
from typing import Optional

class AiEventCreate(BaseModel):
    event_type: str  # forecast, anomaly, query, alert
    branch_code: str
    data: dict
    reference_id: Optional[str] = None

class AiEventReview(BaseModel):
    status: str  # accepted, dismissed, reviewed

class GenericResponse(BaseModel):
    success: bool = True
    data: Optional[dict | list] = None
    error: Optional[str] = None
