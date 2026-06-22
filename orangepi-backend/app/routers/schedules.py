from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel
from app.models.schemas import ScheduleCreate, ScheduleUpdate
from app.auth import get_current_user
from app.database import (get_schedules, insert_schedule, update_schedule,
                           delete_schedule, toggle_schedule, catat_log)

router = APIRouter()
tags = ["Schedules"]

class ToggleRequest(BaseModel):
    status: str

@router.get("/schedules")
async def list_schedules(_=Depends(get_current_user)):
    rows = get_schedules()
    return [{
        "id": row["id"],
        "nama_jadwal": row["nama_jadwal"],
        "waktu_putar": row["waktu_putar"],
        "teks": row["teks"],
        "is_active": bool(row["is_active"]),
    } for row in rows]

@router.post("/schedules")
async def create_schedule(req: ScheduleCreate, _=Depends(get_current_user)):
    insert_schedule(req.nama_jadwal, req.waktu_putar, req.audio_id)
    catat_log("sistem", "Jadwal Ditambahkan", f"Nama: {req.nama_jadwal} pada {req.waktu_putar}", "Selesai")
    return {"success": True, "message": "Jadwal berhasil ditambahkan"}

@router.put("/schedules/{schedule_id}")
async def edit_schedule(schedule_id: int, req: ScheduleUpdate, _=Depends(get_current_user)):
    update_schedule(schedule_id, req.nama_jadwal, req.waktu_putar)
    return {"success": True, "message": "Jadwal berhasil diubah"}

@router.delete("/schedules/{schedule_id}")
async def hapus_schedule(schedule_id: int, _=Depends(get_current_user)):
    delete_schedule(schedule_id)
    catat_log("sistem", "Jadwal Dihapus", f"Jadwal ID {schedule_id} dihapus.", "System")
    return {"success": True, "message": "Jadwal berhasil dihapus"}

@router.post("/schedules/{schedule_id}/toggle")
async def toggle_schedule_endpoint(schedule_id: int, req: ToggleRequest, _=Depends(get_current_user)):
    is_active = 1 if req.status == "on" else 0
    toggle_schedule(schedule_id, is_active)
    status_teks = "diaktifkan" if is_active else "dinonaktifkan"
    catat_log("sistem", "Status Jadwal Diubah", f"Jadwal ID {schedule_id} {status_teks}.", "System")
    return {"success": True, "message": f"Jadwal berhasil {status_teks}!"}
