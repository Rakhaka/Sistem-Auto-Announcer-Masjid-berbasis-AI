# API Documentation — Announcer Pro

Base URL: `http://IP-ORANGE:5000/api` (via Tailscale) atau `https://domain-anda.com/api` (via Cloudflare + Nginx)

Semua endpoint (kecuali login) memerlukan JWT token di header `Authorization: Bearer <token>`.

---

## Auth

### POST `/api/login`
Login untuk mendapatkan JWT token.

**Request:**
```json
{
  "username": "admin",
  "password": "password"
}
```

**Response (200):**
```json
{
  "token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer"
}
```

**Error (401):**
```json
{
  "detail": "Username atau password salah"
}
```

### POST `/api/verify`
Cek validitas token yang sedang dipakai.

**Headers:** `Authorization: Bearer <token>`

**Response (200):**
```json
{
  "valid": true,
  "sub": "admin"
}
```

---

## Health & Status

### GET `/api/health`
Cek apakah backend hidup.

**Response (200):**
```json
{
  "status": "ok",
  "version": "2.0.0"
}
```

### GET `/api/status`
Status lengkap Orange Pi.

**Response (200):**
```json
{
  "online": true,
  "playing": false,
  "mixer_on": false,
  "volume": 75,
  "platform": "Orange Pi",
  "gpio_available": false
}
```

---

## Announce

### POST `/api/announce`
Kirim pengumuman baru. Bisa via teks (TTS) atau audio_id yang sudah ada.

**Request (dengan teks):**
```json
{
  "message": "Perhatian, rapat akan dimulai lima menit lagi.",
  "zone": "lab-1",
  "priority": "normal"
}
```

**Request (dengan audio yang sudah ada):**
```json
{
  "audio_id": 5,
  "zone": "masjid-1",
  "priority": "high"
}
```

**Response (200):**
```json
{
  "success": true,
  "message": "Pengumuman sedang diputar",
  "jobId": "ann-a1b2c3"
}
```

### POST `/api/stop`
Hentikan semua audio yang sedang diputar.

**Response (200):**
```json
{
  "success": true,
  "message": "Semua audio dihentikan"
}
```

### GET `/api/history`
Riwayat pengumuman yang sudah dijalankan (50 log terakhir).

**Response (200):**
```json
[
  {
    "id": 1,
    "kategori": "jadwal",
    "pesan": "Pengumuman: Test",
    "detail": "Zone: lab-1",
    "tanggal": "22 Jun 2026",
    "jam": "16:09",
    "status": "Berhasil"
  }
]
```

---

## Playback

### POST `/api/play-murottal`
Putar streaming surah.

**Request (JSON):**
```json
{
  "url_audio": "https://equran.nos.wjv-1.neo.id/audio-full/Abdullah-Al-Jaloo/001.mp3|Surah Al-Fatihah"
}
```

**Response (200):**
```json
{
  "status": "playing",
  "playing": true,
  "nama": "Surah Al-Fatihah",
  "mixer_on": true
}
```

### POST `/api/set-volume`
Set volume audio.

**Request:**
```json
{
  "volume": 75
}
```

**Response:**
```json
{
  "volume": 75
}
```

### POST `/api/toggle-mixer`
Toggle relay mixer ON/OFF.

**Response:**
```json
{
  "status": "sukses",
  "is_on": true
}
```

### GET `/api/playback-status`
Cek status playback saat ini.

**Response:**
```json
{
  "playing": false,
  "volume": 75,
  "mixer_on": false
}
```

### GET `/api/mixer-status`
Cek status mixer saja.

**Response:**
```json
{
  "is_on": false
}
```

---

## Studio (AI & Upload)

### POST `/api/proses-suara`
Generate audio dari teks via ElevenLabs TTS.

**Request:**
```json
{
  "nama_audio": "Pengumuman Jumat",
  "teks": "Perhatian seluruh jamaah..."
}
```

**Response:**
```json
{
  "success": true,
  "filename": "Pengumuman_Jumat_160930.mp3",
  "message": "Audio 'Pengumuman Jumat' berhasil dibuat!"
}
```

### POST `/api/upload-audio`
Upload file audio manual. **Multipart form-data.**

- Field: `file` — file MP3/WAV/OGG

**Response:**
```json
{
  "success": true,
  "filename": "Upload_160930_audio.mp3",
  "message": "Audio berhasil diupload!"
}
```

### GET `/api/audio-list`
Daftar semua audio yang tersedia di library.

**Response:**
```json
[
  {
    "id": 1,
    "nama_file": "Pengumuman_Jumat_160930.mp3",
    "teks": "Perhatian seluruh jamaah...",
    "waktu_dibuat": "2026-06-22 16:09"
  }
]
```

### DELETE `/api/audio/{audio_id}`
Hapus audio dari library.

**Response:**
```json
{
  "success": true,
  "message": "Audio berhasil dihapus"
}
```

---

## Data (External API)

### GET `/api/prayer-times`
Jadwal sholat dari API Aladhan (di-cache 6 jam).

**Response:**
```json
{
  "jadwal": {
    "Fajr": "04:30",
    "Dhuhr": "12:00",
    "Asr": "15:15",
    "Maghrib": "18:00",
    "Isha": "19:15"
  },
  "tanggal_masehi": "22 Jun 2026",
  "tanggal_hijriah": "7 Muharram 1448 H",
  "sholat_aktif": "Isha"
}
```

### GET `/api/surah-list`
Daftar surah dari EQuran API.

**Response:** Array surah dengan field `nomor`, `namaLatin`, `audioFull`, dll.

---

## Schedules (Jadwal)

### GET `/api/schedules`
Daftar semua jadwal pengumuman.

**Response:**
```json
[
  {
    "id": 1,
    "nama_jadwal": "Adzan Maghrib",
    "waktu_putar": "18:00",
    "teks": "Audio Maghrib...",
    "is_active": true
  }
]
```

### POST `/api/schedules`
Tambah jadwal baru.

**Request:**
```json
{
  "nama_jadwal": "Adzan Maghrib",
  "waktu_putar": "18:00",
  "audio_id": 5
}
```

**Response:**
```json
{
  "success": true,
  "message": "Jadwal berhasil ditambahkan"
}
```

### PUT `/api/schedules/{schedule_id}`
Edit jadwal.

**Request:**
```json
{
  "nama_jadwal": "Adzan Maghrib Updated",
  "waktu_putar": "18:05"
}
```

### DELETE `/api/schedules/{schedule_id}`
Hapus jadwal.

### POST `/api/schedules/{schedule_id}/toggle`
Aktifkan/nonaktifkan jadwal.

**Request:**
```json
{
  "status": "on"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Jadwal berhasil diaktifkan"
}
```

---

## Audio Files

### GET `/api/audio/{filename}`
Serve file audio untuk preview di browser.

Contoh: `GET /api/audio/Pengumuman_Jumat_160930.mp3`

Response: file MP3 dengan `Content-Type: audio/mpeg`.

---

## Logs

### GET `/api/logs`
Semua log sistem (max 50).

**Response:** Array log dengan `id`, `kategori`, `pesan`, `detail`, `tanggal`, `jam`, `status`.

### GET `/api/recent-logs`
3 log terbaru (untuk dashboard).

---

## Auto-generated Docs

Backend FastAPI menyediakan dokumentasi interaktif:

- **Swagger UI:** `http://IP-TAILSCALE:5000/api/docs`
- **ReDoc:** `http://IP-TAILSCALE:5000/api/redoc`

---

## Skema Autentikasi

```
Login:
  POST /api/login { username, password }
  → { token: "eyJ..." }

Setiap request:
  GET /api/health
  Headers: Authorization: Bearer <token>

Jika token expire/ invalid → 401 Unauthorized
```

Token berlaku 24 jam (konfigurasi via `JWT_EXPIRE_HOURS` di `.env`).
