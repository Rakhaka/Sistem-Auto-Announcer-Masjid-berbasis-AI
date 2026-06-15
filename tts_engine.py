import requests
from config import ELEVENLABS_API_KEY, ELEVENLABS_VOICE_ID, ELEVENLABS_MODEL, EDGE_TTS_VOICE


def buat_suara_edge(teks, path_file):
    import asyncio
    import edge_tts
    suara = EDGE_TTS_VOICE
    communicate = edge_tts.Communicate(teks, suara)
    asyncio.run(communicate.save(path_file))


def buat_suara_elevenlabs(teks, path_file):
    print(f"\n[AI] Mengirim teks ke ElevenLabs: {teks[:20]}...")
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{ELEVENLABS_VOICE_ID}"
    headers = {
        "Accept": "audio/mpeg",
        "Content-Type": "application/json",
        "xi-api-key": ELEVENLABS_API_KEY
    }
    data = {
        "text": teks,
        "model_id": ELEVENLABS_MODEL,
        "voice_settings": {
            "stability": 0.5,
            "similarity_boost": 0.7
        }
    }
    try:
        response = requests.post(url, json=data, headers=headers)
        if response.status_code == 200:
            with open(path_file, 'wb') as f:
                f.write(response.content)
            print("[AI] Berhasil! Suara ElevenLabs tersimpan.")
        else:
            print(f"[AI-ERROR] Gagal dari API: {response.text}")
    except Exception as e:
        print(f"[AI-ERROR] Kesalahan koneksi: {e}")
