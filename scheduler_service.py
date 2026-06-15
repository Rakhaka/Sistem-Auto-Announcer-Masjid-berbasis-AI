from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from database import get_active_schedules_by_time, catat_log
from audio_player import play_audio_with_delay, nyalakan_mixer_aman, set_scheduler

scheduler = BackgroundScheduler()

def cek_jadwal():
    waktu_sekarang = datetime.now().strftime("%H:%M")
    jadwal_aktif = get_active_schedules_by_time(waktu_sekarang)

    for jdwl in jadwal_aktif:
        print(f"\n[ALARM] Memutar jadwal: {jdwl['nama_jadwal']} pada {waktu_sekarang}")
        nyalakan_mixer_aman(mode="auto")
        play_audio_with_delay(jdwl['nama_file'], delay=3)
        catat_log("jadwal", f"Jadwal {jdwl['nama_jadwal']} Berbunyi", f"Memutar audio: {jdwl['nama_file'][:30]}...", "Berhasil")

def start_scheduler():
    set_scheduler(scheduler)
    scheduler.add_job(func=cek_jadwal, trigger="cron", minute="*")
    scheduler.start()
