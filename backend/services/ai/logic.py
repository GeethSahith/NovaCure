from database import get_admin_client

def log_ai_event(event_data: dict) -> dict:
    """Simulate generating an AI insight, anomaly flag, or forecast."""
    admin = get_admin_client()
    res = admin.table("ai_events").insert(event_data).execute()
    if not res.data:
        raise Exception("Failed to log AI event")
    return res.data[0]

def get_pending_events(branch_code: str = None) -> list[dict]:
    """Fetch all pending AI recommendations for human-in-the-loop review."""
    admin = get_admin_client()
    query = admin.table("ai_events").select("*").eq("status", "pending")
    if branch_code:
        query = query.eq("branch_code", branch_code)
        
    res = query.order("created_at", desc=True).execute()
    return res.data or []

def review_ai_event(event_id: str, new_status: str) -> dict:
    """Human-in-the-loop: Accept or dismiss the AI's recommendation."""
    admin = get_admin_client()
    res = admin.table("ai_events").update({"status": new_status}).eq("id", event_id).execute()
    if not res.data:
        raise Exception(f"AI Event {event_id} not found")
    return res.data[0]

def generate_strategic_insights() -> str:
    """Call the Bytez SDK and use Llama-3.1 to generate real supply chain insights."""
    import os
    import json
    from bytez import Bytez
    from services.reporting import logic as report_logic

    # 1. Fetch live data mathematically
    revenue = report_logic.get_revenue_analytics()
    risk = report_logic.get_expiry_risk()
    
    from .prompts import BUSINESS_INSIGHTS_PROMPT_TEMPLATE
    
    # 2. Format custom prompt via template
    prompt = BUSINESS_INSIGHTS_PROMPT_TEMPLATE.format(
        revenue_data=json.dumps(revenue),
        risk_data=json.dumps(risk)
    )

    # 3. Trigger Generative AI via Bytez
    bytez_key = os.getenv("BYTEZ_API_KEY")
    if not bytez_key:
        return "⚠️ Error: BYTEZ_API_KEY not found in environment."

    try:
        sdk = Bytez(bytez_key)
        model = sdk.model("meta-llama/Meta-Llama-3.1-8B-Instruct")
        
        results = model.run([{"role": "user", "content": prompt}])
        if getattr(results, 'error', None):
            return f"⚠️ Bytez SDK Error: {results.error}"
            
        output = results.output
        if isinstance(output, list) and len(output) > 0:
            output = output[0]
            
        if isinstance(output, dict) and "content" in output:
            return output["content"]
            
        return str(output)
    except Exception as e:
        return f"⚠️ Failed to connect to Bytez LLM: {str(e)}"
