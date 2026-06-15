import os
import sys
from config import AUDIO_DIR
from database import init_db, catat_log
from scheduler_service import start_scheduler
from app import app

if __name__ == '__main__':
    if not os.path.exists(AUDIO_DIR):
        os.makedirs(AUDIO_DIR)

    init_db()
    catat_log("sistem", "Sistem Dinyalakan", "Server Announcer Pro Berhasil Booting.", "System")
    start_scheduler()

    print("\n[SYSTEM] Announcer Pro siap! Menggunakan Waitress WSGI server...")
    print("[SYSTEM] Buka http://localhost:80 atau http://IP-ORANGE-PI:80 di browser\n")

    try:
        from waitress import serve
        serve(app, host='0.0.0.0', port=80)
    except PermissionError:
        print("[ERROR] Port 80 butuh akses Administrator di Windows.")
        print("[SYSTEM] Mencoba port 5000 sebagai alternatif...\n")
        serve(app, host='0.0.0.0', port=5000)
