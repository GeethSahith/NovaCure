from fastapi import APIRouter, Depends, HTTPException
from schemas.ai import AiEventCreate, AiEventReview, GenericResponse
from services.ai import logic
from dependencies import get_current_user, require_manager

router = APIRouter(prefix="/ai", tags=["AI & Alerts"])

@router.post("/events", response_model=GenericResponse)
async def generate_ai_event(req: AiEventCreate, current_user: dict = Depends(get_current_user)):
    """Generate a simulated background AI event (anomaly/forecast)."""
    try:
        data = logic.log_ai_event(req.model_dump())
        return GenericResponse(success=True, data=data)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/events", response_model=GenericResponse)
async def fetch_insights(current_user: dict = Depends(get_current_user)):
    """Fetch pending AI events. Managers see globally, others see local branch."""
    if current_user["role"] in ["admin", "regional_manager"]:
        data = logic.get_pending_events()
    else:
        data = logic.get_pending_events(branch_code=current_user.get("branch_code"))
        
    return GenericResponse(success=True, data={"events": data})

@router.put("/events/{event_id}/review", response_model=GenericResponse)
async def review_insight(event_id: str, req: AiEventReview, current_user: dict = Depends(require_manager)):
    """Regional Manager / Admin strictly: Approve or reject an AI anomaly recommendation."""
    if req.status not in ["accepted", "dismissed"]:
        raise HTTPException(status_code=400, detail="Status must be 'accepted' or 'dismissed'")
        
    try:
        data = logic.review_ai_event(event_id, req.status)
        return GenericResponse(success=True, data=data)
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.get("/business-insights", response_model=GenericResponse)
async def generate_business_insights(current_user: dict = Depends(require_manager)):
    """Regional Manager / Admin strictly: Use Bytez Llama-3.1 to analyze entire DB."""
    try:
        insights = logic.generate_strategic_insights()
        return GenericResponse(success=True, data={"insights": insights})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
