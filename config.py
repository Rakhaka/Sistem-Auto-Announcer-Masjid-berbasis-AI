import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_NAME = os.path.join(BASE_DIR, 'masjid.db')
AUDIO_DIR = os.path.join(BASE_DIR, 'suara_tersimpan')

PIN_RELAY = 7

ELEVENLABS_API_KEY = "sk_acfabe5beae2839c59468f619a1c73608e0c25f1469d12b9"
ELEVENLABS_VOICE_ID = "IKne3meq5aSn9XLyUdCD"
ELEVENLABS_MODEL = "eleven_multilingual_v2"

EDGE_TTS_VOICE = "id-ID-ArdiNeural"

ALADHAN_API_URL = "http://api.aladhan.com/v1/timingsByCity?city=Pangkalpinang&country=Indonesia&method=11"
EQURAN_API_URL = "https://equran.id/api/v2/surat"

LOGIN_USERNAME = "admin"
LOGIN_PASSWORD = "password"
SECRET_KEY = "announcer-pro-secret-key-2024"

AUDIO_CACHE_TTL = 21600
SURAH_CACHE_TTL = 86400
