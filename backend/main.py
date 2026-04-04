"""
NovaCure Pharmacy Operations Platform — API Gateway
Single FastAPI app that mounts all service routers.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from services.auth.routes import router as auth_router
from services.inventory.routes import router as inventory_router
from services.sales.routes import router as sales_router

app = FastAPI(
    title="NovaCure Platform",
    description="Pharmacy Operations Platform — Phase 2 Backend",
    version="1.0.0",
)

# ── CORS (allow frontend during development) ─────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Mount service routers ─────────────────────────────────
app.include_router(auth_router)
app.include_router(inventory_router)
app.include_router(sales_router)
# app.include_router(purchase_router)
# app.include_router(ai_router)


# ── Root & health ─────────────────────────────────────────

@app.get("/")
def root():
    return {"message": "Welcome to the NovaCure Platform"}


@app.get("/health")
def health():
    return {"status": "ok"}
