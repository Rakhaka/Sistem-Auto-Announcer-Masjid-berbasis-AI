from fastapi import APIRouter, Depends, HTTPException, Request
from app.models.schemas import PlayMurottalRequest, SetVolumeRequest
from app.auth import get_current_user
from app.audio_player import (stop_audio, is_playing, is_mixer_on,
                               set_volume, get_volume, play_audio_with_delay,
                               nyalakan_mixer_aman, matikan_mixer_aman)
from app.database import catat_log

router = APIRouter()
tags = ["Playback"]

@router.post("/play-murottal")
async def play_murottal(req: Request, _=Depends(get_current_user)):
    data = await req.json() if req.headers.get("content-type") == "application/json" else {}
    url_raw = data.get("url_audio") or req.query_params.get("url_audio")
    if not url_raw:
        raise HTTPException(status_code=400, detail="url_audio required")
    parts = url_raw.split("|", 1)
    url_audio = parts[0]
    nama_surah = parts[1] if len(parts) > 1 else "Surah Pilihan"
    if is_playing():
        stop_audio()
        catat_log("murottal", f"Murottal {nama_surah} Dihentikan", "Dimatikan manual.", "Berhasil")
        return {"status": "stopped", "playing": False}
    nyalakan_mixer_aman(mode="auto")
    play_audio_with_delay(url_audio, delay=3)
    catat_log("murottal", f"Murottal {nama_surah} Diputar", "Memutar manual di Masjid.", "Berhasil")
    return {"status": "playing", "playing": True, "nama": nama_surah, "mixer_on": is_mixer_on()}

@router.post("/set-volume")
async def set_volume_endpoint(req: SetVolumeRequest, _=Depends(get_current_user)):
    level = set_volume(req.volume)
    return {"volume": level}

@router.post("/toggle-mixer")
async def toggle_mixer(_=Depends(get_current_user)):
    if is_mixer_on():
        matikan_mixer_aman()
        catat_log("sistem", "Mixer Dimatikan", "Dimatikan manual via Dashboard.", "Selesai")
    else:
        nyalakan_mixer_aman(mode="manual")
        catat_log("sistem", "Mixer Dinyalakan", "Dinyalakan manual via Dashboard.", "Selesai")
    return {"status": "sukses", "is_on": is_mixer_on()}

@router.get("/playback-status")
async def playback_status(_=Depends(get_current_user)):
    return {"playing": is_playing(), "volume": get_volume(), "mixer_on": is_mixer_on()}

@router.get("/mixer-status")
async def mixer_status(_=Depends(get_current_user)):
    return {"is_on": is_mixer_on()}
