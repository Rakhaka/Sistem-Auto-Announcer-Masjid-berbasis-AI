from datetime import datetime
from fastapi import APIRouter, Depends
from app.auth import get_current_user
from app.api_service import get_data_masjid, get_daftar_surah_fresh, get_daftar_surah

router = APIRouter()
tags = ["Data"]

@router.get("/prayer-times")
async def prayer_times(_=Depends(get_current_user)):
    jadwal, tanggal_masehi, tanggal_hijriah = get_data_masjid()
    if not jadwal:
        return {"error": "Gagal memuat jadwal"}
    waktu_sekarang = datetime.now().strftime("%H:%M")
    sholat_aktif = "Isha"
    if waktu_sekarang >= jadwal['Fajr'] and waktu_sekarang < jadwal['Dhuhr']:
        sholat_aktif = 'Fajr'
    elif waktu_sekarang >= jadwal['Dhuhr'] and waktu_sekarang < jadwal['Asr']:
        sholat_aktif = 'Dhuhr'
    elif waktu_sekarang >= jadwal['Asr'] and waktu_sekarang < jadwal['Maghrib']:
        sholat_aktif = 'Asr'
    elif waktu_sekarang >= jadwal['Maghrib'] and waktu_sekarang < jadwal['Isha']:
        sholat_aktif = 'Maghrib'
    return {
        "jadwal": jadwal,
        "tanggal_masehi": tanggal_masehi,
        "tanggal_hijriah": tanggal_hijriah,
        "sholat_aktif": sholat_aktif,
    }

@router.get("/surah-list")
async def surah_list(_=Depends(get_current_user)):
    surah = get_daftar_surah_fresh()
    return surah
