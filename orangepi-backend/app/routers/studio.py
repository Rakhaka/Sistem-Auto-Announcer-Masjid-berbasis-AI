import os
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from werkzeug.utils import secure_filename
from app.models.schemas import ProsesSuaraRequest, UploadResponse
from app.auth import get_current_user
from app.database import get_audio_list, insert_audio, delete_audio, catat_log
from app.tts_engine import buat_suara_elevenlabs
from app.config import AUDIO_DIR

router = APIRouter()
tags = ["Studio"]

ALLOWED_EXTENSIONS = {"mp3", "wav", "ogg"}

def allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

@router.post("/proses-suara")
async def proses_suara(req: ProsesSuaraRequest, _=Depends(get_current_user)):
    nama_bersih = req.nama_audio.replace(" ", "_")
    timestamp = datetime.now().strftime("%H%M%S")
    filename = f"{nama_bersih}_{timestamp}.mp3"
    filepath = os.path.join(AUDIO_DIR, filename)
    buat_suara_elevenlabs(req.teks, filepath)
    insert_audio(filename, req.teks)
    catat_log("ai", f"Audio '{req.nama_audio}' Dibuat", f"Teks: {req.teks[:30]}...", "Selesai")
    return {"success": True, "filename": filename, "message": f"Audio '{req.nama_audio}' berhasil dibuat!"}

@router.post("/upload-audio", response_model=UploadResponse)
async def upload_audio(file: UploadFile = File(...), _=Depends(get_current_user)):
    if not file.filename:
        raise HTTPException(status_code=400, detail="File tidak valid")
    if not allowed_file(file.filename):
        raise HTTPException(status_code=400, detail="Format tidak didukung. Hanya MP3/WAV/OGG")
    nama_asli = secure_filename(file.filename)
    timestamp = datetime.now().strftime("%H%M%S")
    nama_file = f"Upload_{timestamp}_{nama_asli}"
    filepath = os.path.join(AUDIO_DIR, nama_file)
    content = await file.read()
    with open(filepath, "wb") as f:
        f.write(content)
    insert_audio(nama_file, "Audio Hasil Upload Manual")
    catat_log("sistem", "Audio Diupload", f"File {nama_asli} berhasil diupload.", "Selesai")
    return UploadResponse(success=True, filename=nama_file, message="Audio berhasil diupload!")

@router.get("/audio-list")
async def audio_list(_=Depends(get_current_user)):
    rows = get_audio_list(only_local=True)
    return [{
        "id": row["id"],
        "nama_file": row["nama_file"],
        "teks": row["teks"],
        "waktu_dibuat": row["waktu_dibuat"],
    } for row in rows]

@router.delete("/audio/{audio_id}")
async def hapus_audio(audio_id: int, _=Depends(get_current_user)):
    nama_file = delete_audio(audio_id)
    if not nama_file:
        raise HTTPException(status_code=404, detail="Audio tidak ditemukan")
    catat_log("sistem", "Audio Dihapus", f"File {nama_file[:20]} dihapus.", "System")
    return {"success": True, "message": "Audio berhasil dihapus"}
