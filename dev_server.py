"""
Development Server — Announcer Pro
Backend API (port 5000) + Frontend + Proxy (port 3000) dalam satu perintah.

Cara pakai:
    python dev_server.py

Lalu buka: http://localhost:3000

Frontend di :3000, tapi request /api/* dan /api/audio/* otomatis
di-forward ke backend di :5000. Jadi nol CORS issue.
"""

import subprocess
import sys
import os
import signal
import time
import threading

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.join(BASE_DIR, "orangepi-backend")

backend_proc = None
proxy_proc = None

def run_backend():
    global backend_proc
    os.chdir(BACKEND_DIR)
    backend_proc = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "5000"],
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
    )
    for line in backend_proc.stdout:
        print(f"[BACKEND] {line}", end="")

def run_proxy():
    global proxy_proc
    proxy_script = os.path.join(BASE_DIR, "proxy_server.py")
    if not os.path.exists(proxy_script):
        print("[ERROR] proxy_server.py tidak ditemukan!")
        return
    proxy_proc = subprocess.Popen(
        [sys.executable, proxy_script],
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
    )
    for line in proxy_proc.stdout:
        print(f"[PROXY]  {line}", end="")

def cleanup(signum=None, frame=None):
    print("\n[SYSTEM] Mematikan semua server...")
    for p in [backend_proc, proxy_proc]:
        if p and p.poll() is None:
            p.terminate()
            p.wait()
    print("[SYSTEM] Semua server dimatikan.")
    sys.exit(0)

if __name__ == "__main__":
    signal.signal(signal.SIGINT, cleanup)
    signal.signal(signal.SIGTERM, cleanup)

    print("=" * 50)
    print("  Announcer Pro — Development Server")
    print("=" * 50)
    print(f"  Buka    : http://localhost:3000")
    print(f"  Backend : http://localhost:5000")
    print(f"  API Docs: http://localhost:5000/api/docs")
    print(f"  [Ctrl+C] untuk berhenti")
    print("=" * 50)

    t1 = threading.Thread(target=run_backend, daemon=True)
    t2 = threading.Thread(target=run_proxy, daemon=True)

    t1.start()
    time.sleep(3)
    t2.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        cleanup()
