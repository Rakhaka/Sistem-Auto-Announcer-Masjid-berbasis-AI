import os
import vlc
import time
import threading
from datetime import datetime, timedelta
from app.config import PIN_RELAY, AUDIO_DIR
try:
    import OPi.GPIO as GPIO
    import orangepi.pi3
    GPIO.setwarnings(False)
    GPIO.setmode(orangepi.pi3.BOARD)
    GPIO.setup(PIN_RELAY, GPIO.OUT)
    GPIO.output(PIN_RELAY, GPIO.LOW)
    _GPIO_AVAILABLE = True
except (ImportError, ModuleNotFoundError):
    _GPIO_AVAILABLE = False
    print("[SYSTEM] GPIO tidak tersedia (mode simulasi)")

player_masjid = vlc.MediaPlayer()

MIXER_MENYALA = False
AUTO_OFF_JOB_ID = 'job_auto_off'
_scheduler_instance = None

def set_scheduler(scheduler):
    global _scheduler_instance
    _scheduler_instance = scheduler

def nyalakan_mixer_aman(mode="auto"):
    global MIXER_MENYALA
    if not MIXER_MENYALA:
        MIXER_MENYALA = True
        print(f"\n[RELAY] Mengirim sinyal ke Pin {PIN_RELAY} -> MIXER MENYALA")
        if _GPIO_AVAILABLE:
            GPIO.output(PIN_RELAY, GPIO.HIGH)
    if mode == "auto":
        atur_timer_auto_off(30)
    elif mode == "manual":
        batalkan_timer_auto_off()

def matikan_mixer_aman():
    global MIXER_MENYALA
    if MIXER_MENYALA:
        print("\n[RELAY] Menghentikan audio sebelum mematikan listrik...")
        player_masjid.stop()
        time.sleep(2)
        MIXER_MENYALA = False
        print("[RELAY] Memutus arus dari Pin -> MIXER MATI")
        if _GPIO_AVAILABLE:
            GPIO.output(PIN_RELAY, GPIO.LOW)
        batalkan_timer_auto_off()

def atur_timer_auto_off(menit):
    global _scheduler_instance
    batalkan_timer_auto_off()
    waktu_mati = datetime.now() + timedelta(minutes=menit)
    if _scheduler_instance:
        _scheduler_instance.add_job(
            func=matikan_mixer_aman_otomatis,
            trigger='date',
            run_date=waktu_mati,
            id=AUTO_OFF_JOB_ID,
            replace_existing=True
        )
        print(f"[SISTEM] Timer Auto-Off disetel. Mixer otomatis mati pada {waktu_mati.strftime('%H:%M:%S')}")

def batalkan_timer_auto_off():
    global _scheduler_instance
    if _scheduler_instance:
        try:
            if _scheduler_instance.get_job(AUTO_OFF_JOB_ID):
                _scheduler_instance.remove_job(AUTO_OFF_JOB_ID)
                print("[SISTEM] Timer Auto-Off dibatalkan.")
        except:
            pass

def matikan_mixer_aman_otomatis():
    print("\n[SISTEM] Waktu Auto-Off 30 menit tiba. Mematikan Mixer otomatis...")
    matikan_mixer_aman()
    from app.database import catat_log
    catat_log("sistem", "Mixer Otomatis Mati", "Timer 30 menit setelah jadwal selesai.", "System")

def stop_audio():
    player_masjid.stop()

def is_playing():
    return player_masjid.is_playing()

def is_mixer_on():
    return MIXER_MENYALA

def set_volume(level):
    level = max(0, min(100, level))
    player_masjid.audio_set_volume(level)
    return level

def get_volume():
    return player_masjid.audio_get_volume()

def play_audio_with_delay(media_source, delay=3):
    if isinstance(media_source, str):
        if not media_source.startswith('http'):
            media_source = os.path.abspath(os.path.join(AUDIO_DIR, media_source))
        media = vlc.Media(media_source)
    else:
        media = media_source
    player_masjid.set_media(media)
    player_masjid.audio_set_volume(100)

    def _delayed_play():
        time.sleep(delay)
        player_masjid.play()

    t = threading.Thread(target=_delayed_play, daemon=True)
    t.start()
