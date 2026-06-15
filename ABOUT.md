# Announcer Pro

**Sistem Kontrol Audio Masjid Otomatis berbasis Web**

Announcer Pro adalah sistem dashboard web untuk mengontrol audio masjid secara terpusat. Dibangun untuk berjalan di **Orange Pi 3 LTS** (ARM), sistem ini menggantikan perangkat keras manual (amplifier, pemutar MP3, timer) dengan satu antarmuka web modern yang dapat diakses dari HP/laptop.

---

## Fitur Utama

### 1. Dashboard Real-time
- **Jadwal Sholat** — ditampilkan dalam 5 kartu (Subuh, Dzuhur, Ashar, Maghrib, Isya) dengan highlight waktu aktif. Data dari API Aladhan, di-cache 6 jam agar tidak lemot.
- **Murottal Control** — putar streaming Surah dari EQuran (Syekh Mishary Rasyid) langsung ke speaker masjid. Tombol Play/Pause toggle, volume slider.
- **Mixer ON/OFF** — kontrol relay GPIO untuk menyalakan/mematikan mixer audio masjid. Timer auto-off 30 menit.
- **Stop Audio (Panic)** — hentikan semua audio yang sedang berbunyi di toa masjid.
- **Aktivitas Terkini** — log 3 kejadian terakhir, auto-refresh tiap 30 detik via AJAX.
- **Navigation Shortcuts** — akses cepat ke Studio AI dan Atur Pengumuman.

### 2. Studio AI
- **Generate Audio** — ketik teks pengumuman, AI ElevenLabs ubah jadi suara natural berbahasa Indonesia (model `eleven_multilingual_v2`). Auto-generate file `.mp3`.
- **Upload Manual** — unggah rekaman sendiri (MP3/WAV/OGG) untuk digabungkan ke pustaka.
- **Pustaka Audio** — daftar semua audio yang tersedia, lengkap dengan preview play di browser (tidak masuk mixer masjid).
- **Voice Fallback** — jika ElevenLabs gagal, sistem siap menggunakan `edge-tts` (gratis, offline-compatible).

### 3. Atur Pengumuman (Scheduler)
- **Buat Jadwal Baru** — tentukan nama, pilih audio (dari pustaka atau streaming surah), set waktu putar.
- **Daftar Jadwal** — tabel semua jadwal dengan toggle aktif/nonaktif, edit, dan hapus.
- **Eksekusi Otomatis** — APScheduler mengecek setiap menit (`cron minute="*"`). Saat waktu tiba: mixer dinyalakan, audio diputar setelah delay 3 detik (hindari jegleg), timer auto-off 30 menit.

### 4. Log Sistem
- Riwayat lengkap semua aktivitas: murottal, jadwal, generate AI, sistem.
- Filter visual dengan ikon per kategori.

### 5. Keamanan
- Login session (`admin/password`).
- Semua route diproteksi decorator `@login_required`.
- Secret key untuk session Flask.

---

## Arsitektur Sistem

```
┌──────────────────────────────────────────────────────────────┐
│                        Web Browser                           │
│            (HP/Laptop Admin — Tailwind CSS + AJAX)           │
└─────────────────────────┬────────────────────────────────────┘
                          │ HTTP
┌─────────────────────────▼────────────────────────────────────┐
│                    Waitress WSGI Server                       │
│                     (Multi-threaded)                          │
│                                                              │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────────┐ │
│  │ app.py   │  │ auth.py  │  │ config.py│  │ database.py  │ │
│  │ (routes) │  │ (login)  │  │ (setting)│  │ (SQLite CRUD)│ │
│  └────┬─────┘  └──────────┘  └──────────┘  └──────┬───────┘ │
│       │                                           │         │
│  ┌────▼───────────────────────────────────────────▼───────┐ │
│  │              Modular Services Layer                     │ │
│  │                                                         │ │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │ │
│  │  │audio_player  │  │tts_engine    │  │api_service   │  │ │
│  │  │(VLC + GPIO)  │  │(ElevenLabs)  │  │(Aladhan+     │  │ │
│  │  │              │  │              │  │ EQuran)      │  │ │
│  │  └──────┬───────┘  └──────────────┘  └──────────────┘  │ │
│  │         │                                               │ │
│  │  ┌──────▼───────┐                                       │ │
│  │  │scheduler     │                                       │ │
│  │  │(APScheduler) │                                       │ │
│  │  └──────────────┘                                       │ │
│  └─────────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────┘
         │                              │
         ▼                              ▼
  ┌────────────┐               ┌────────────────┐
  │ VLC Media  │               │  GPIO Relay    │
  │ Player     │──────────────►│  (Pin 7)       │
  │ (Output    │               │  ─► Mixer ON/OFF│
  │  ke mixer) │               └────────────────┘
  └────────────┘
```

## Alur Kerja

### Play Murottal Manual
1. Admin pilih surah → klik Play.
2. Backend: `nyalakan_mixer_aman(mode="auto")` → GPIO HIGH (mixer ON).
3. Set timer auto-off 30 menit via APScheduler.
4. Thread terpisah: tunggu 3 detik → `player_masjid.play()` (hindari jegleg).
5. Response JSON `{playing: true, mixer_on: true}` → JS update UI.

### Jadwal Otomatis
1. Scheduler `cek_jadwal()` jalan setiap menit.
2. Query `get_active_schedules_by_time(waktu_sekarang)`.
3. Jika cocok: `nyalakan_mixer_aman(mode="auto")` + `play_audio_with_delay(file, delay=3)`.
4. Timer auto-off 30 menit.
5. Log dicatat ke database.

### Generate Audio AI
1. Admin ketik teks → submit form `/proses_suara`.
2. Backend panggil ElevenLabs TTS API → simpan `.mp3` ke `suara_tersimpan/`.
3. `insert_audio()` ke database, catat log.
4. Redirect ke Studio UI → auto-play preview di browser (HTML5 `<audio>`, TIDAK lewat VLC/mixer).

---

## Teknologi

| Komponen | Teknologi |
|----------|-----------|
| **Backend** | Python 3.9+, Flask 3.0 |
| **Frontend** | Tailwind CSS (lokal), Space Grotesk + Inter fonts |
| **WSGI Server** | Waitress 3.0 (multi-threaded) |
| **Database** | SQLite 3 |
| **Audio Player** | python-vlc 3.0 |
| **TTS Engine** | ElevenLabs API (plus edge-tts cadangan) |
| **External API** | Aladhan (jadwal sholat), EQuran (daftar surah) |
| **Scheduler** | APScheduler 3.10 |
| **GPIO** | OPi.GPIO (Orange Pi) |
| **Relay** | GPIO Pin 7 (BCM) — kontrol mixer |

---

## Struktur File

```
announcer_pro/
├── run.py                 # Entry point: init DB, start scheduler, serve via Waitress
├── app.py                 # Route handlers (Flask) — ~322 baris
├── config.py              # Semua konstanta (API key, PIN relay, path, credentials)
├── database.py            # Operasi SQLite (CRUD audio, jadwal, logs)
├── audio_player.py        # VLC player, mixer relay, delayed play, volume
├── tts_engine.py          # ElevenLabs text-to-speech API
├── api_service.py         # API Aladhan + EQuran dengan caching in-memory
├── scheduler_service.py   # APScheduler, cek jadwal tiap menit
├── auth.py                # Decorator @login_required
├── requirements.txt       # Dependencies Python
├── announcer-pro.service  # Systemd service (auto-start di Orange Pi)
├── ABOUT.md               # Dokumentasi ini
├── masjid.db              # Database SQLite (auto-generated)
├── suara_tersimpan/       # Folder audio files (.mp3, .wav, .ogg)
├── static/
│   └── js/
│       └── tailwind.js    # Tailwind CSS lokal (~407KB)
└── templates/
    ├── base.html          # Layout utama (sidebar dark, topnav, bottom nav mobile)
    ├── dashboard.html     # Halaman utama: jadwal sholat, murottal, logs
    ├── studio.html        # Studio AI: generate, upload, pustaka audio
    ├── manajemen.html     # CRUD jadwal pengumuman
    ├── login.html         # Halaman login
    └── logs.html          # Riwayat aktivitas sistem
```

---

## Cara Pakai

### Login
- Buka `http://IP-ORANGE-PI:80` di browser.
- Masuk dengan username `admin`, password `password`.

### Dashboard
- Lihat **Jadwal Sholat** — waktu aktif otomatis ter-highlight.
- **Play Murottal** — pilih surah, klik tombol play. Status mixer otomatis ON.
- **Volume** — klik icon speaker, geser slider.
- **Mixer** — toggle ON/OFF manual.
- **Stop Audio** — hentikan semua audio (panic button).

### Studio AI
- **Generate** — isi nama + teks, klik "Generate & Simpan". Audio otomatis terputar di browser.
- **Upload** — pilih file MP3/WAV/OGG, klik upload.
- **Pustaka** — preview play (browser saja, tidak ke mixer), hapus audio.

### Atur Pengumuman
- **Buat Jadwal** — pilih nama, tipe suara (library/murottal), file, waktu.
- **Daftar Jadwal** — toggle aktif/mati, edit, hapus.
- Eksekusi otomatis saat waktu tiba.

### Log
- Riwayat lengkap semua aktivitas sistem.

---

## Deploy ke Orange Pi 3 LTS

### 1. Install System Dependencies
```bash
sudo apt update
sudo apt install -y python3 python3-pip python3-venv vlc vlc-bin git
```

### 2. Clone & Setup
```bash
git clone <repo-url> /home/orangepi/announcer_pro
cd /home/orangepi/announcer_pro
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

### 3. GPIO Relay
Pastikan `OPi.GPIO` terinstall (ada di requirements.txt).  
Relay terhubung ke **GPIO Pin 7** (konfigurasi di `config.py`).  
Saat server jalan: `GPIO.output(PIN_RELAY, GPIO.HIGH)` = mixer ON, `GPIO.LOW` = mixer OFF.

### 4. Audio Output
Set default audio ke 3.5mm jack (bukan HDMI):
```bash
sudo alsamixer        # Atur output
amixer cset numid=3 1 # 1=jack 3.5mm, 2=HDMI
```

### 5. Systemd Service (Auto-start)
```bash
sudo cp announcer-pro.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable announcer-pro
sudo systemctl start announcer-pro
```

Cek status:
```bash
sudo systemctl status announcer-pro
journalctl -u announcer-pro -f  # lihat log real-time
```

### 6. Firewall
```bash
sudo ufw allow 80/tcp
sudo ufw allow 5000/tcp
```

### 7. Akses
Buka browser → `http://IP-ORANGE-PI:80` atau `http://IP-ORANGE-PI:5000` (fallback).

---

## API Endpoints

### Public (setelah login)
| Route | Method | Fungsi |
|-------|--------|--------|
| `/` | GET | Dashboard utama |
| `/studio` | GET | Halaman Studio AI |
| `/manajemen` | GET | Halaman manajemen jadwal |
| `/logs` | GET | Halaman log sistem |
| `/login` | GET/POST | Login |

### API (AJAX JSON)
| Route | Method | Fungsi |
|-------|--------|--------|
| `/api/prayer-times` | GET | Jadwal sholat + tanggal |
| `/api/recent-logs` | GET | 3 log terbaru |
| `/api/surah-list` | GET | Daftar surah dari EQuran |
| `/api/playback-status` | GET | Status play, volume, mixer |

### Actions
| Route | Method | Fungsi |
|-------|--------|--------|
| `/play_murottal` | POST | Putar streaming surah |
| `/stop_audio` | POST | Hentikan semua audio |
| `/set_volume` | POST | Set volume (0-100) |
| `/toggle_mixer` | POST | Toggle mixer ON/OFF |
| `/get_mixer_status` | GET | Cek status mixer |
| `/proses_suara` | POST | Generate audio AI |
| `/upload_audio` | POST | Upload file audio |
| `/hapus_audio/<id>` | GET | Hapus audio |
| `/tambah_jadwal` | POST | Tambah jadwal baru |
| `/edit_jadwal` | POST | Edit jadwal |
| `/hapus_jadwal/<id>` | GET | Hapus jadwal |
| `/toggle_jadwal/<id>` | POST | Aktif/nonaktif jadwal |
| `/suara/<filename>` | GET | Serve file audio |
| `/logout` | GET | Logout |

---

## Optimasi Performa

### Di sisi Backend
- **Caching in-memory** — jadwal sholat di-cache 6 jam, daftar surah 24 jam. Tidak perlu request API tiap halaman di-refresh.
- **Threading untuk delayed play** — `_delayed_play()` jalan di `daemon=True` thread, Flask response instan.
- **Waitress multi-threaded** — handle banyak request concurrent tanpa blok.
- **Getter `is_mixer_on()`** — hindari bug immutable variable saat import.

### Di sisi Frontend
- **AJAX polling** — ganti `window.location.reload()` dengan `fetch()` periodik (60s prayer, 30s logs, 15s playback). Bandwidth minimal.
- **Tailwind lokal** — `static/js/tailwind.js` (~407KB) — tidak perlu CDN, offline-friendly.
- **Font Google di-cache browser** — Google Fonts diload sekali, browser cache.
- **Tanpa library berat** — tidak ada jQuery, React, Vue. Vanilla JS + Tailwind.
- **Tanpa efek GPU-heavy** — tidak ada backdrop-filter, blur, atau animasi CSS kompleks.

---

## Troubleshooting

### Server tidak bisa bind port 80
Fallback otomatis ke port 5000. Akses via `http://IP:5000`.

### GPIO error di Windows
GPIO otomatis terdeteksi tidak tersedia (mode simulasi). Relay tidak aktif, fungsi lain tetap jalan.

### VLC tidak bisa play audio
Pastikan VLC terinstall: `sudo apt install vlc vlc-bin`.  
Cek audio device: `vlc --audio-device-list`.

### API jadwal sholat gagal
Cek koneksi internet. Data di-cache 6 jam — jika sebelumnya pernah sukses, data lama tetap dipakai.

### Mixer tidak mati otomatis
Timer auto-off 30 menit diatur via APScheduler. Jika server restart, timer di-reset. Matikan manual via tombol Mixer atau Stop Audio.

---

## Lisensi

Announcer Pro — Sistem Internal Masjid.  
Dikembangkan untuk kebutuhan operasional audio masjid.
