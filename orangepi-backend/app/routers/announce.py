import os
import uuid
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from app.models.schemas import AnnounceRequest, AnnounceResponse, StopResponse
from app.auth import get_current_user
from app.database import insert_audio, catat_log
from app.audio_player import play_audio_with_delay, stop_audio as stop_player, nyalakan_mixer_aman, matikan_mixer_aman
from app.tts_engine import buat_suara_elevenlabs
from app.config import AUDIO_DIR

router = APIRouter()
tags = ["Announce"]

@router.post("/announce", response_model=AnnounceResponse)
async def announce(req: AnnounceRequest, _=Depends(get_current_user)):
    job_id = f"ann-{uuid.uuid4().hex[:6]}"
    if req.audio_id:
        from app.database import get_audio_by_id
        audio = get_audio_by_id(req.audio_id)
        if not audio:
            raise HTTPException(status_code=404, detail="Audio not found")
        filename = audio["nama_file"]
    elif req.message:
        timestamp = datetime.now().strftime("%H%M%S")
        safe_name = f"announce_{timestamp}_{uuid.uuid4().hex[:4]}.mp3"
        filepath = os.path.join(AUDIO_DIR, safe_name)
        buat_suara_elevenlabs(req.message, filepath)
        insert_audio(safe_name, req.message)
        filename = safe_name
    else:
        raise HTTPException(status_code=400, detail="message or audio_id required")
    nyalakan_mixer_aman(mode="auto")
    play_audio_with_delay(filename, delay=3)
    catat_log("jadwal", f"Pengumuman: {req.message or filename}", f"Zone: {req.zone}", "Berhasil")
    return AnnounceResponse(success=True, message="Pengumuman sedang diputar", jobId=job_id)

@router.post("/stop", response_model=StopResponse)
async def stop_announce(_=Depends(get_current_user)):
    stop_player()
    matikan_mixer_aman()
    catat_log("sistem", "Pengumuman Dihentikan", "Dihentikan via API.", "System")
    return StopResponse(success=True, message="Semua audio dihentikan")

@router.get("/history")
async def announce_history(_=Depends(get_current_user)):
    from app.database import get_all_logs
    logs = get_all_logs(50)
    return [{
        "id": log["id"],
        "kategori": log["kategori"],
        "pesan": log["pesan"],
        "detail": log["detail"],
        "tanggal": log["tanggal"],
        "jam": log["jam"],
        "status": log["status"],
    } for log in logs]
