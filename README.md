# Announcer Pro

**Sistem Kontrol Audio Masjid Otomatis — Frontend + Backend Terpisah**

Announcer Pro adalah sistem dashboard web untuk mengontrol audio masjid secara terpusat. Sistem ini menggunakan arsitektur frontend/backend terpisah: backend berjalan di Orange Pi (masjid), frontend statis di-deploy di server lab dengan domain publik.

---

## Arsitektur

```
Browser → Cloudflare Tunnel → Lab Server (Nginx) → Tailscale → Orange Pi (API :5000) → Speaker
```

- **Backend:** FastAPI + JWT auth, VLC audio, GPIO relay, APScheduler, SQLite
- **Frontend:** HTML + Tailwind + Vanilla JS (statis, zero framework)
- **Koneksi:** Tailscale VPN — Orange Pi tidak perlu port forwarding

---

## Struktur Project

```
announcer-project/
├── orangepi-backend/        # API server — deploy di Orange Pi
│   ├── app/
│   │   ├── main.py          # FastAPI entry point
│   │   ├── config.py        # Konfigurasi dari .env
│   │   ├── auth.py          # JWT authentication
│   │   ├── database.py      # SQLite CRUD
│   │   ├── audio_player.py  # VLC player + GPIO relay
│   │   ├── tts_engine.py    # ElevenLabs TTS
│   │   ├── api_service.py   # Aladhan + EQuran API
│   │   ├── scheduler_service.py  # APScheduler
│   │   └── routers/         # Endpoint REST
│   ├── suara_tersimpan/     # Audio files
│   ├── requirements.txt
│   ├── .env.example
│   └── announcer-api.service
│
├── frontend-dashboard/      # Static SPA — deploy di Lab Server
│   ├── index.html           # Dashboard utama
│   ├── login.html           # Login JWT
│   ├── studio.html          # Studio AI
│   ├── manajemen.html       # Manajemen jadwal
│   ├── logs.html            # Log sistem
│   └── js/
│       ├── tailwind.js
│       ├── api.js            # Fetch wrapper with JWT
│       └── auth.js           # Login/logout/token
│
├── docs/
│   └── API.md
├── ABOUT.md
├── IMPLEMENTATION_PLAN.md
└── README.md
```

---

## Quick Start (Backend — Orange Pi)

```bash
# 1. Install dependencies
sudo apt update
sudo apt install -y python3 python3-pip python3-venv vlc vlc-bin git

# 2. Install Tailscale
curl -fsSL https://tailscale.com/install.sh | sh
sudo tailscale up --auth-key=KEY_DARI_ADMIN --hostname=orange-announcer

# 3. Clone & setup
git clone <repo-url> /home/orangepi/announcer-backend
cd /home/orangepi/announcer-backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
nano .env   # Isi konfigurasi

# 4. Systemd service
sudo cp announcer-api.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable announcer-api
sudo systemctl start announcer-api

# 5. Cek
curl http://localhost:5000/api/health
```

---

## Endpoints Utama

| Method | Endpoint | Fungsi |
|--------|----------|--------|
| POST | `/api/login` | Login → JWT token |
| GET | `/api/health` | Cek backend hidup |
| GET | `/api/status` | Status Orange Pi & speaker |
| POST | `/api/announce` | Kirim pengumuman |
| POST | `/api/stop` | Hentikan audio |
| GET | `/api/history` | Riwayat pengumuman |
| GET | `/api/prayer-times` | Jadwal sholat |
| GET | `/api/surah-list` | Daftar surah |
| POST | `/api/proses-suara` | Generate audio AI |
| POST | `/api/upload-audio` | Upload file audio |
| POST | `/api/play-murottal` | Putar streaming surah |
| POST | `/api/toggle-mixer` | Toggle relay mixer |
| GET | `/api/schedules` | Daftar jadwal |
| GET | `/api/logs` | Log sistem |

Dokumentasi lengkap: `docs/API.md`

Dokumentasi interaktif (Swagger): `http://IP-TAILSCALE:5000/api/docs`

---

## Tech Stack

| Komponen | Teknologi |
|----------|-----------|
| Backend | Python 3.9+, FastAPI, Uvicorn |
| Frontend | Tailwind CSS, Vanilla JS |
| Database | SQLite |
| Audio | python-vlc 3.0 |
| TTS | ElevenLabs API + edge-tts |
| Scheduler | APScheduler |
| GPIO | OPi.GPIO (Orange Pi) |
| VPN | Tailscale (WireGuard) |
| Tunnel | Cloudflare Tunnel |
