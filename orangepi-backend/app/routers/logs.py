from fastapi import APIRouter, Depends
from app.auth import get_current_user
from app.database import get_recent_logs, get_all_logs

router = APIRouter()
tags = ["Logs"]

@router.get("/logs")
async def list_logs(_=Depends(get_current_user)):
    rows = get_all_logs(50)
    return [{
        "id": row["id"],
        "kategori": row["kategori"],
        "pesan": row["pesan"],
        "detail": row["detail"],
        "tanggal": row["tanggal"],
        "jam": row["jam"],
        "status": row["status"],
    } for row in rows]

@router.get("/recent-logs")
async def recent_logs(_=Depends(get_current_user)):
    rows = get_recent_logs(3)
    return [{
        "kategori": row["kategori"],
        "pesan": row["pesan"],
        "detail": row["detail"],
        "jam": row["jam"],
        "tanggal": row["tanggal"],
        "status": row["status"],
    } for row in rows]
