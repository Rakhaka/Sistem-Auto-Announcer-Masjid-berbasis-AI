import time
import requests
from config import ALADHAN_API_URL, EQURAN_API_URL, AUDIO_CACHE_TTL, SURAH_CACHE_TTL

_api_cache = {}

def _cached_get(key, ttl, fetch_func):
    now = time.time()
    if key in _api_cache:
        cached = _api_cache[key]
        if now - cached['time'] < ttl:
            return cached['data']
    data = fetch_func()
    if data is not None:
        _api_cache[key] = {'data': data, 'time': now}
    return data

def _fetch_prayer_times():
    try:
        response = requests.get(ALADHAN_API_URL, timeout=10)
        if response.status_code == 200:
            data = response.json()['data']
            jadwal = data['timings']
            tanggal_masehi = data['date']['readable']
            hijri_data = data['date']['hijri']
            tanggal_hijriah = f"{hijri_data['day']} {hijri_data['month']['en']} {hijri_data['year']} H"
            return jadwal, tanggal_masehi, tanggal_hijriah
    except Exception as e:
        print("Error API Aladhan:", e)
    return None

def get_data_masjid():
    result = _cached_get('prayer_times', AUDIO_CACHE_TTL, _fetch_prayer_times)
    if result:
        return result
    return None, None, None

def _fetch_surah_list():
    try:
        response = requests.get(EQURAN_API_URL, timeout=15)
        if response.status_code == 200:
            return response.json()['data']
    except Exception as e:
        print("Error API Murottal:", e)
    return None

def get_daftar_surah():
    result = _cached_get('surah_list', SURAH_CACHE_TTL, _fetch_surah_list)
    if result:
        return result
    return []

def get_daftar_surah_fresh():
    result = _fetch_surah_list()
    if result:
        _api_cache['surah_list'] = {'data': result, 'time': time.time()}
        return result
    if 'surah_list' in _api_cache:
        return _api_cache['surah_list']['data']
    return []
