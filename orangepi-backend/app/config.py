import os
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env'))

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SECRET_KEY = os.getenv("APP_SECRET_KEY", "announcer-pro-secret-key-2024")
APP_PORT = int(os.getenv("APP_PORT", "5000"))

ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "password")
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "announcer-pro-jwt-secret-2024")
JWT_EXPIRE_HOURS = int(os.getenv("JWT_EXPIRE_HOURS", "24"))

AUDIO_DIR = os.path.join(BASE_DIR, os.getenv("AUDIO_DIR", "suara_tersimpan"))
PIN_RELAY = int(os.getenv("PIN_RELAY", "7"))

ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY", "")
ELEVENLABS_VOICE_ID = os.getenv("ELEVENLABS_VOICE_ID", "IKne3meq5aSn9XLyUdCD")
ELEVENLABS_MODEL = os.getenv("ELEVENLABS_MODEL", "eleven_multilingual_v2")
EDGE_TTS_VOICE = os.getenv("EDGE_TTS_VOICE", "id-ID-ArdiNeural")

ALADHAN_API_URL = os.getenv("ALADHAN_API_URL", "http://api.aladhan.com/v1/timingsByCity?city=Pangkalpinang&country=Indonesia&method=11")
EQURAN_API_URL = os.getenv("EQURAN_API_URL", "https://equran.id/api/v2/surat")

AUDIO_CACHE_TTL = int(os.getenv("AUDIO_CACHE_TTL", "21600"))
SURAH_CACHE_TTL = int(os.getenv("SURAH_CACHE_TTL", "86400"))

DB_NAME = os.path.join(BASE_DIR, os.getenv("DB_NAME", "masjid.db"))
