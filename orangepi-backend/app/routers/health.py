from fastapi import APIRouter, Depends
from app.models.schemas import HealthResponse
from app.auth import get_current_user

router = APIRouter()
tags = ["Health"]

@router.get("/health", response_model=HealthResponse)
async def health_check(_=Depends(get_current_user)):
    return HealthResponse(status="ok", version="2.0.0")
