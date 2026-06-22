import os
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from app.auth import get_current_user
from app.config import AUDIO_DIR

router = APIRouter()
tags = ["Audio"]

@router.get("/audio/{filename:path}")
async def serve_audio(filename: str, _=Depends(get_current_user)):
    filepath = os.path.normpath(os.path.join(AUDIO_DIR, filename))
    if not filepath.startswith(os.path.normpath(AUDIO_DIR)):
        raise HTTPException(status_code=403, detail="Akses ditolak")
    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail="File tidak ditemukan")
    return FileResponse(filepath, media_type="audio/mpeg")
