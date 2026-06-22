from fastapi import APIRouter, Depends, HTTPException
from app.models.schemas import LoginRequest, TokenResponse
from app.auth import verify_password, create_access_token, get_current_user

router = APIRouter()
tags = ["Auth"]

@router.post("/login", response_model=TokenResponse)
async def login(req: LoginRequest):
    if not verify_password(req.username, req.password):
        raise HTTPException(status_code=401, detail="Username atau password salah")
    token = create_access_token()
    return TokenResponse(token=token)

@router.post("/verify")
async def verify_token(user=Depends(get_current_user)):
    return {"valid": True, "sub": user.get("sub")}
