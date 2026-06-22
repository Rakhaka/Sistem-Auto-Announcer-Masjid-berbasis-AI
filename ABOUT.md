# Announcer Pro

**Sistem Kontrol Audio Masjid Otomatis — Arsitektur Frontend/Backend Terpisah**

Announcer Pro adalah sistem dashboard web untuk mengontrol audio masjid secara terpusat. Sistem ini telah di-**refactor dari arsitektur monolitik menjadi Frontend + Backend terpisah** sehingga lebih fleksibel, aman, dan bisa diakses dari domain publik tanpa membuka Orange Pi ke internet.

---

## Arsitektur Sistem

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           Browser (HP/Laptop)                           │
│                    https://domain-anda.com/dashboard                     │
└────────────────────────────────┬────────────────────────────────────────┘
                                 │ HTTPS
┌────────────────────────────────▼────────────────────────────────────────┐
│                        Cloudflare Tunnel                                  │
│                    (Security, SSL, DDoS Protection)                       │
└────────────────────────────────┬────────────────────────────────────────┘
                                 │ Internal Network
┌────────────────────────────────▼────────────────────────────────────────┐
│                          Nginx — Lab Server                               │
│                                                                          │
│  ┌─────────────────────┐  ┌─────────────────────┐  ┌─────────────────┐  │
│  │   Static Files      │  │  /api/* Proxy        │  │ /suara/* Proxy │  │
│  │   (HTML, JS, CSS)   │  │  ─► Tailscale ─►     │  │ ─► Tailscale   │  │
│  │   Served langsung    │  │  Orange Pi :5000     │  │ Orange Pi :5000│  │
│  └─────────────────────┘  └─────────────────────┘  └─────────────────┘  │
└────────────────────────────────┬────────────────────────────────────────┘
                                 │ Tailscale VPN (WireGuard)
┌────────────────────────────────▼────────────────────────────────────────┐
│                        Orange Pi 3 LTS (Masjid)                          │
│                                                                          │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │                    Backend API Server (:5000)                     │   │
│  │                                                                  │   │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌────────────────┐   │   │
│  │  │ auth.py  │  │config.py │  │database  │  │ api_service    │   │   │
│  │  │ (JWT)    │  │(.env)    │  │ (SQLite) │  │ (Aladhan,      │   │   │
│  │  │          │  │          │  │          │  │  EQuran)       │   │   │
│  │  └──────────┘  └──────────┘  └──────────┘  └────────────────┘   │   │
│  │                                                                  │   │
│  │  ┌──────────────┐  ┌──────────────┐  ┌────────────────────┐     │   │
│  │  │audio_player  │  │tts_engine    │  │scheduler_service   │     │   │
│  │  │(VLC + GPIO)  │  │(ElevenLabs)  │  │(APScheduler)       │     │   │
│  │  └──────┬───────┘  └──────────────┘  └────────────────────┘     │   │
│  └─────────┼────────────────────────────────────────────────────────┘   │
│            │                                                            │
│            ▼                                                            │
│     ┌────────────┐          ┌────────────────┐                         │
│     │ VLC Media  │          │  GPIO Relay    │                         │
│     │ Player     │─────────►│  (Pin 7)       │                         │
│     │ (Output    │          │  ─► Mixer ON/OFF│                         │
│     │  ke mixer) │          └────────────────┘                         │
│     └────────────┘                                                     │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Alur Data

### Request dari Dashboard (contoh: Putar Pengumuman)

1. User klik "Putar" di dashboard → JavaScript panggil `POST /api/announce`
2. Browser kirim request ke **domain publik** (`https://announcer.domain.com/api/announce`) dengan header `Authorization: Bearer <token>`
3. Cloudflare Tunnel terima request → forward ke **Lab Server**
4. Nginx cocokkan pattern `/api/*` → **proxy_pass** ke `http://100.x.x.x:5000/api/announce` via **Tailscale**
5. **Orange Pi Backend** terima request:
   - Validasi JWT token
   - Jika tipe `text`: panggil ElevenLabs TTS → simpan `.mp3`
   - Nyalakan relay mixer (GPIO)
   - Putar audio via VLC dengan delay 3 detik
   - Catat log ke SQLite
   - Return JSON `{ success: true, jobId: "ann-001" }`
6. Response balik lewat jalur yang sama → browser update UI

### Keamanan
- **Orange Pi tidak punya IP publik** — hanya di dalam Tailscale
- **Tidak perlu port forwarding** — semua koneksi inbound dari Lab Server via Tailscale
- **Autentikasi JWT** — setiap request API diverifikasi signature token
- **Domain publik** hanya指向 Lab Server, bukan Orange Pi
- **Cloudflare Tunnel** — SSL, DDoS protection, hide origin server

---

## Perubahan dari Versi Monolitik

| Aspek | Sebelum (Monolit) | Sesudah (Frontend + Backend) |
|-------|-------------------|------------------------------|
| **Server** | Satu Flask serve semuanya | Backend API terpisah, Frontend static |
| **Auth** | Flask session (cookie) | JWT token (stateless) |
| **Frontend** | Jinja2 SSR (server-side render) | SPA static (HTML + JS fetch API) |
| **Deploy Frontend** | Di Orange Pi | Di Lab Server (domain publik) |
| **Deploy Backend** | Di Orange Pi | Tetap di Orange Pi |
| **Akses** | IP Orange Pi langsung | Domain publik → Cloudflare → Lab Server → Tailscale → Orange Pi |
| **CORS** | Same-origin (tidak masalah) | Frontend domain berbeda → backend perlu CORS |
| **Database** | SQLite di Orange Pi | Tetap SQLite di Orange Pi (via API) |
| **Audio files** | Di Orange Pi | Tetap di Orange Pi (proxy via Nginx) |

---

## Struktur File (Final)

```
announcer-project/
├── orangepi-backend/             # Backend API — di-deploy ke Orange Pi
│   ├── app/
│   │   ├── main.py               # Entry point FastAPI
│   │   ├── config.py             # Konfigurasi dari .env
│   │   ├── auth.py               # JWT authentication
│   │   ├── database.py           # SQLite CRUD operations
│   │   ├── audio_player.py       # VLC player + GPIO relay
│   │   ├── tts_engine.py         # ElevenLabs + edge-tts
│   │   ├── api_service.py        # Aladhan + EQuran API
│   │   ├── scheduler_service.py  # APScheduler
│   │   └── routers/
│   │       ├── health.py
│   │       ├── status.py
│   │       ├── announce.py
│   │       ├── playback.py
│   │       ├── studio.py
│   │       ├── schedules.py
│   │       ├── logs.py
│   │       └── audio.py
│   ├── suara_tersimpan/          # Audio files (.mp3, .wav, .ogg)
│   ├── requirements.txt
│   ├── .env
│   └── announcer-api.service     # Systemd (auto-start)
│
├── frontend-dashboard/           # Frontend static — di-deploy ke Lab Server
│   ├── index.html                # Dashboard utama
│   ├── login.html                # Login dengan JWT
│   ├── studio.html               # Studio AI
│   ├── manajemen.html            # Manajemen jadwal
│   ├── logs.html                 # Log sistem
│   ├── js/
│   │   ├── tailwind.js
│   │   ├── api.js                # Fetch wrapper dengan JWT
│   │   └── auth.js               # Login/logout/token
│   └── assets/
│
├── docs/
│   └── API.md                    # Dokumentasi endpoint
│
├── .env.example
├── IMPLEMENTATION_PLAN.md
└── README.md
```

---

## Fitur Utama

### 1. Dashboard Real-time
- **Jadwal Sholat** — 5 kartu (Subuh, Dzuhur, Ashar, Maghrib, Isya) dengan highlight waktu aktif. Data dari API Aladhan, di-cache 6 jam.
- **Murottal Control** — putar streaming Surah dari EQuran (Syekh Mishary Rasyid) langsung ke speaker masjid. Tombol Play/Pause toggle, volume slider.
- **Mixer ON/OFF** — kontrol relay GPIO untuk menyalakan/mematikan mixer audio. Timer auto-off 30 menit.
- **Stop Audio (Panic)** — hentikan semua audio yang sedang berbunyi.
- **Aktivitas Terkini** — log 3 kejadian terakhir, auto-refresh tiap 30 detik.
- **Navigation Shortcuts** — akses cepat ke Studio AI dan Atur Pengumuman.

### 2. Studio AI
- **Generate Audio** — ketik teks, AI ElevenLabs ubah jadi suara natural Indonesia.
- **Upload Manual** — unggah rekaman sendiri (MP3/WAV/OGG).
- **Pustaka Audio** — daftar semua audio, preview play di browser.
- **Voice Fallback** — edge-tts (gratis, offline-compatible) jika ElevenLabs gagal.

### 3. Atur Pengumuman (Scheduler)
- **Buat Jadwal Baru** — nama, pilih audio, set waktu putar.
- **Daftar Jadwal** — tabel dengan toggle aktif/nonaktif, edit, hapus.
- **Eksekusi Otomatis** — APScheduler cek tiap menit. Saat waktu tiba: mixer ON → delay 3 detik → play audio → auto-off 30 menit.

### 4. Log Sistem
- Riwayat lengkap semua aktivitas: murottal, jadwal, generate AI, sistem.
- Filter visual per kategori.

### 5. Keamanan (JWT)
- Login via API → dapat JWT token.
- Setiap request API wajib sertakan `Authorization: Bearer <token>`.
- Token expire 24 jam.
- Backend hanya bisa diakses via Tailscale.

---

## Teknologi

| Komponen | Teknologi |
|----------|-----------|
| **Backend API** | Python 3.9+, FastAPI |
| **Frontend** | HTML + Tailwind CSS + Vanilla JS |
| **Web Server (Frontend)** | Nginx (Lab Server) |
| **Tunnel** | Cloudflare Tunnel |
| **VPN** | Tailscale (WireGuard) |
| **Database** | SQLite 3 |
| **Audio Player** | python-vlc 3.0 |
| **TTS Engine** | ElevenLabs API + edge-tts cadangan |
| **External API** | Aladhan (jadwal sholat), EQuran (daftar surah) |
| **Scheduler** | APScheduler 3.10 |
| **GPIO** | OPi.GPIO (Orange Pi) |
| **Relay** | GPIO Pin 7 (BCM) — kontrol mixer |

---

## Cara Deploy

### Backend (Orange Pi)

#### 1. Install System Dependencies
```bash
sudo apt update
sudo apt install -y python3 python3-pip python3-venv vlc vlc-bin git
```

#### 2. Install Tailscale
```bash
curl -fsSL https://tailscale.com/install.sh | sh
sudo tailscale up --auth-key=KEY_DARI_ADMIN --hostname=orange-announcer
```

#### 3. Clone & Setup Backend
```bash
git clone <repo-url> /home/orangepi/announcer-backend
cd /home/orangepi/announcer-backend
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
cp .env.example .env
nano .env   # Isi konfigurasi
```

#### 4. GPIO Relay
Relay terhubung ke GPIO Pin 7. Pastikan OPi.GPIO terinstall.

#### 5. Audio Output
```bash
amixer cset numid=3 1  # 1=jack 3.5mm, 2=HDMI
```

#### 6. Systemd Service (Auto-start)
```bash
sudo cp announcer-api.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable announcer-api
sudo systemctl start announcer-api
```

#### 7. Cek Status
```bash
sudo systemctl status announcer-api
journalctl -u announcer-api -f
```

### Frontend (Lab Server)

#### 1. Copy static files
```bash
cp -r frontend-dashboard/* /var/www/announcer/
```

#### 2. Nginx Configuration
```nginx
server {
    listen 80;
    server_name announcer.domain.com;

    root /var/www/announcer;
    index index.html;

    # Static files
    location / {
        try_files $uri $uri/ /index.html;
    }

    # API proxy ke Orange Pi via Tailscale
    location /api/ {
        proxy_pass http://TAILSCALE-IP:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }

    # Audio files proxy
    location /suara/ {
        proxy_pass http://TAILSCALE-IP:5000;
        proxy_set_header Host $host;
    }
}
```

#### 3. Cloudflare Tunnel
```bash
cloudflared tunnel create announcer
cloudflared tunnel route dns announcer announcer.domain.com
cloudflared tunnel run announcer
```

---

## API Endpoints

### Auth
| Method | Endpoint | Fungsi |
|--------|----------|--------|
| POST | `/api/login` | Login, dapat JWT token |
| POST | `/api/verify` | Cek validitas token |

### Health & Status
| Method | Endpoint | Fungsi |
|--------|----------|--------|
| GET | `/api/health` | Cek backend hidup |
| GET | `/api/status` | Status Orange Pi, speaker, mixer |

### Announcement
| Method | Endpoint | Fungsi |
|--------|----------|--------|
| POST | `/api/announce` | Kirim pengumuman (TTS → play) |
| POST | `/api/stop` | Hentikan semua audio |
| GET | `/api/history` | Riwayat pengumuman |

### Playback
| Method | Endpoint | Fungsi |
|--------|----------|--------|
| POST | `/api/play-murottal` | Putar streaming surah |
| POST | `/api/set-volume` | Set volume (0-100) |
| POST | `/api/toggle-mixer` | Toggle mixer ON/OFF |
| GET | `/api/playback-status` | Status play, volume, mixer |

### Studio
| Method | Endpoint | Fungsi |
|--------|----------|--------|
| POST | `/api/proses-suara` | Generate audio AI |
| POST | `/api/upload-audio` | Upload file audio |
| GET | `/api/audio-list` | Daftar audio library |
| DELETE | `/api/audio/{id}` | Hapus audio |

### Data
| Method | Endpoint | Fungsi |
|--------|----------|--------|
| GET | `/api/prayer-times` | Jadwal sholat + tanggal |
| GET | `/api/surah-list` | Daftar surah dari EQuran |

### Schedules
| Method | Endpoint | Fungsi |
|--------|----------|--------|
| GET | `/api/schedules` | Daftar jadwal |
| POST | `/api/schedules` | Tambah jadwal baru |
| PUT | `/api/schedules/{id}` | Edit jadwal |
| DELETE | `/api/schedules/{id}` | Hapus jadwal |
| POST | `/api/schedules/{id}/toggle` | Aktif/nonaktif jadwal |

### Audio
| Method | Endpoint | Fungsi |
|--------|----------|--------|
| GET | `/api/audio/{filename}` | Serve audio file preview |

### Logs
| Method | Endpoint | Fungsi |
|--------|----------|--------|
| GET | `/api/logs` | Semua log (limit 50) |
| GET | `/api/recent-logs` | 3 log terbaru |

---

## Lisensi

Announcer Pro — Sistem Internal Masjid.  
Dikembangkan untuk kebutuhan operasional audio masjid.
