from fastapi import APIRouter, Depends, HTTPException
from schemas.reporting import GenericResponse, AnalyticsResponse
from services.reporting import logic
from dependencies import require_manager

router = APIRouter(prefix="/reports", tags=["Business Intelligence"])

@router.get("/dashboard", response_model=GenericResponse)
async def get_bi_dashboard(current_user: dict = Depends(require_manager)):
    """Regional Manager or Admin strictly: Fetch company-wide holistic numbers."""
    try:
        revenue = logic.get_revenue_analytics()
        risk = logic.get_expiry_risk()
        
        payload = AnalyticsResponse(
            revenue_data=revenue,
            expiry_risk=risk
        )
        return GenericResponse(success=True, data=payload)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
