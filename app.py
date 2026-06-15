import os
from datetime import datetime
from flask import (Flask, render_template, request, redirect,
                   url_for, send_from_directory, jsonify, session)
from werkzeug.utils import secure_filename
from config import AUDIO_DIR, SECRET_KEY, LOGIN_USERNAME, LOGIN_PASSWORD
from database import (init_db, catat_log, get_audio_list, insert_audio,
                      delete_audio, get_schedules, insert_schedule,
                      update_schedule, delete_schedule, toggle_schedule,
                      get_recent_logs, get_all_logs)
from audio_player import (player_masjid, nyalakan_mixer_aman, matikan_mixer_aman,
                          play_audio_with_delay, stop_audio, is_playing, is_mixer_on,
                          set_volume, get_volume)
from tts_engine import buat_suara_elevenlabs
from api_service import get_data_masjid, get_daftar_surah, get_daftar_surah_fresh
from scheduler_service import scheduler
from auth import login_required, ADMIN_USERNAME, ADMIN_PASSWORD

app = Flask(__name__)
app.secret_key = SECRET_KEY

ALLOWED_EXTENSIONS = {'mp3', 'wav', 'ogg'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# ===================== AUTH ROUTES =====================

@app.route('/login', methods=['GET', 'POST'])
def login_page():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session['logged_in'] = True
            next_page = request.args.get('next')
            return redirect(next_page or url_for('home'))
        return render_template('login.html', error="Username atau password salah!")
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('login_page'))

# ===================== API DATA ROUTES (AJAX) =====================

@app.route('/api/prayer-times')
def api_prayer_times():
    jadwal, tanggal_masehi, tanggal_hijriah = get_data_masjid()
    if not jadwal:
        return jsonify({"error": "Gagal memuat jadwal"}), 500

    waktu_sekarang = datetime.now().strftime("%H:%M")
    sholat_aktif = "Isha"
    if waktu_sekarang >= jadwal['Fajr'] and waktu_sekarang < jadwal['Dhuhr']:
        sholat_aktif = 'Fajr'
    elif waktu_sekarang >= jadwal['Dhuhr'] and waktu_sekarang < jadwal['Asr']:
        sholat_aktif = 'Dhuhr'
    elif waktu_sekarang >= jadwal['Asr'] and waktu_sekarang < jadwal['Maghrib']:
        sholat_aktif = 'Asr'
    elif waktu_sekarang >= jadwal['Maghrib'] and waktu_sekarang < jadwal['Isha']:
        sholat_aktif = 'Maghrib'

    return jsonify({
        "jadwal": jadwal,
        "tanggal_masehi": tanggal_masehi,
        "tanggal_hijriah": tanggal_hijriah,
        "sholat_aktif": sholat_aktif
    })

@app.route('/api/recent-logs')
def api_recent_logs():
    logs = get_recent_logs(3)
    data = []
    for log in logs:
        data.append({
            "kategori": log['kategori'],
            "pesan": log['pesan'],
            "detail": log['detail'],
            "jam": log['jam'],
            "tanggal": log['tanggal'],
            "status": log['status']
        })
    return jsonify(data)

@app.route('/api/surah-list')
def api_surah_list():
    surah = get_daftar_surah_fresh()
    return jsonify(surah)

@app.route('/api/playback-status')
def api_playback_status():
    return jsonify({
        "playing": is_playing(),
        "volume": get_volume(),
        "mixer_on": is_mixer_on()
    })

# ===================== MAIN ROUTES =====================

@app.route('/')
@login_required
def home():
    jadwal, tanggal_masehi, tanggal_hijriah = get_data_masjid()
    daftar_surah = get_daftar_surah()
    sholat_aktif = "Isha"

    if jadwal:
        waktu_sekarang = datetime.now().strftime("%H:%M")
        if waktu_sekarang >= jadwal['Fajr'] and waktu_sekarang < jadwal['Dhuhr']:
            sholat_aktif = 'Fajr'
        elif waktu_sekarang >= jadwal['Dhuhr'] and waktu_sekarang < jadwal['Asr']:
            sholat_aktif = 'Dhuhr'
        elif waktu_sekarang >= jadwal['Asr'] and waktu_sekarang < jadwal['Maghrib']:
            sholat_aktif = 'Asr'
        elif waktu_sekarang >= jadwal['Maghrib'] and waktu_sekarang < jadwal['Isha']:
            sholat_aktif = 'Maghrib'

    recent_logs = get_recent_logs(3)

    return render_template('dashboard.html',
                           jadwal=jadwal,
                           tanggal_masehi=tanggal_masehi,
                           tanggal_hijriah=tanggal_hijriah,
                           sholat_aktif=sholat_aktif,
                           daftar_surah=daftar_surah,
                           recent_logs=recent_logs)

# ===================== AUDIO SERVE =====================

@app.route('/suara/<filename>')
@login_required
def serve_audio(filename):
    return send_from_directory(AUDIO_DIR, filename)

# ===================== MUROTTAL & PLAYBACK =====================

@app.route('/play_murottal', methods=['POST'])
@login_required
def play_murottal():
    data_pilihan = request.form.get('url_audio') or request.json.get('url_audio')
    if not data_pilihan:
        return jsonify({"error": "No audio selected"}), 400

    try:
        url_audio, nama_surah = data_pilihan.split('|')
    except ValueError:
        url_audio = data_pilihan
        nama_surah = "Surah Pilihan"

    print(f"\n[STREAMING] Memutar Murottal manual: {nama_surah}")

    if is_playing():
        stop_audio()
        catat_log("murottal", f"Murottal {nama_surah} Dihentikan", f"Dimatikan manual.", "Berhasil")
        return jsonify({"status": "stopped", "playing": False})

    nyalakan_mixer_aman(mode="auto")
    play_audio_with_delay(url_audio, delay=3)
    catat_log("murottal", f"Murottal {nama_surah} Diputar", f"Memutar manual di Masjid.", "Berhasil")
    return jsonify({"status": "playing", "playing": True, "nama": nama_surah, "mixer_on": is_mixer_on()})

@app.route('/stop_audio', methods=['POST'])
@login_required
def stop_audio_route():
    matikan_mixer_aman()
    catat_log("sistem", "Panic Button Ditekan", "Semua audio masjid dihentikan manual.", "System")
    return jsonify({"status": "stopped", "playing": False, "mixer_on": is_mixer_on()})

@app.route('/set_volume', methods=['POST'])
@login_required
def set_volume_route():
    data = request.json
    level = int(data.get('volume', 50))
    level = set_volume(level)
    return jsonify({"volume": level})

# ===================== MIXER CONTROL =====================

@app.route('/toggle_mixer', methods=['POST'])
@login_required
def toggle_mixer():
    if is_mixer_on():
        matikan_mixer_aman()
        catat_log("sistem", "Mixer Dimatikan", "Dimatikan manual via Dashboard.", "Selesai")
    else:
        nyalakan_mixer_aman(mode="manual")
        catat_log("sistem", "Mixer Dinyalakan", "Dinyalakan manual via Dashboard.", "Selesai")
    return jsonify({"status": "sukses", "is_on": is_mixer_on()})

@app.route('/get_mixer_status', methods=['GET'])
@login_required
def get_mixer_status():
    return jsonify({"is_on": is_mixer_on()})

# ===================== STUDIO ROUTES =====================

@app.route('/studio')
@login_required
def studio():
    pesan_sukses = request.args.get('pesan')
    file_baru = request.args.get('file_baru')
    daftar_audio = get_audio_list(only_local=True)
    return render_template('studio.html', pesan=pesan_sukses, daftar_audio=daftar_audio, file_baru=file_baru)

@app.route('/proses_suara', methods=['POST'])
@login_required
def proses_suara():
    nama_audio_raw = request.form.get('nama_audio', 'Pengumuman')
    teks_admin = request.form['teks_pengumuman']
    nama_bersih = nama_audio_raw.replace(" ", "_")
    waktu_sekarang = datetime.now().strftime("%H%M%S")

    nama_file = f"{nama_bersih}_{waktu_sekarang}.mp3"
    path_file = os.path.join(AUDIO_DIR, nama_file)

    buat_suara_elevenlabs(teks_admin, path_file)

    insert_audio(nama_file, teks_admin)
    catat_log("ai", f"Audio '{nama_audio_raw}' Dibuat", f"Teks: {teks_admin[:30]}...", "Selesai")

    return redirect(url_for('studio', pesan=f"Audio '{nama_audio_raw}' berhasil dibuat!", file_baru=nama_file))

@app.route('/upload_audio', methods=['POST'])
@login_required
def upload_audio():
    if 'file_audio' not in request.files:
        return redirect(url_for('studio', pesan="Gagal: Tidak ada file yang dipilih!"))
    file = request.files['file_audio']
    if file.filename == '':
        return redirect(url_for('studio', pesan="Gagal: File kosong!"))
    if file and allowed_file(file.filename):
        nama_asli = secure_filename(file.filename)
        waktu_sekarang = datetime.now().strftime("%H%M%S")
        nama_file = f"Upload_{waktu_sekarang}_{nama_asli}"
        path_simpan = os.path.join(AUDIO_DIR, nama_file)
        file.save(path_simpan)
        insert_audio(nama_file, "Audio Hasil Upload Manual")
        catat_log("sistem", "Audio Diupload", f"File {nama_asli} berhasil diupload.", "Selesai")
        return redirect(url_for('studio', pesan="Audio berhasil diupload!", file_baru=nama_file))
    else:
        return redirect(url_for('studio', pesan="Gagal: Format file tidak didukung! (Hanya MP3/WAV/OGG)"))

@app.route('/hapus_audio/<int:id>')
@login_required
def hapus_audio(id):
    nama_file = delete_audio(id)
    if nama_file:
        catat_log("sistem", "Audio Dihapus", f"File {nama_file[:20]} dihapus.", "System")
        return redirect(url_for('studio', pesan=f"File audio berhasil dihapus!"))
    return redirect(url_for('studio'))

# ===================== SCHEDULE ROUTES =====================

@app.route('/manajemen')
@login_required
def manajemen():
    pesan_sukses = request.args.get('pesan')
    daftar_audio = get_audio_list(only_local=True)
    daftar_jadwal = get_schedules()
    return render_template('manajemen.html',
                           daftar_audio=daftar_audio,
                           daftar_jadwal=daftar_jadwal,
                           pesan=pesan_sukses)

@app.route('/tambah_jadwal', methods=['POST'])
@login_required
def tambah_jadwal():
    nama_jadwal = request.form['nama_jadwal']
    waktu_putar = request.form['waktu_putar']
    tipe_suara = request.form.get('tipe_audio')

    if tipe_suara == 'murottal':
        murottal_raw = request.form.get('audio_id_murottal')
        if murottal_raw and "URL|" in murottal_raw:
            _, url, nama = murottal_raw.split('|')
            audio_id = insert_audio(url, nama)
        else:
            return redirect(url_for('manajemen', pesan="Gagal: Surah belum dipilih!"))
    else:
        audio_id = request.form.get('audio_id_ai')

    insert_schedule(nama_jadwal, waktu_putar, audio_id)
    catat_log("sistem", "Jadwal Ditambahkan", f"Nama: {nama_jadwal} pada {waktu_putar}", "Selesai")
    return redirect(url_for('manajemen', pesan="Jadwal Berhasil Ditambahkan!"))

@app.route('/edit_jadwal', methods=['POST'])
@login_required
def edit_jadwal():
    update_schedule(
        request.form.get('id_jadwal'),
        request.form.get('nama_jadwal'),
        request.form.get('jam')
    )
    return redirect(request.referrer)

@app.route('/hapus_jadwal/<int:id>')
@login_required
def hapus_jadwal(id):
    delete_schedule(id)
    catat_log("sistem", "Jadwal Dihapus", f"Jadwal ID {id} dihapus.", "System")
    return redirect(url_for('manajemen', pesan="Jadwal berhasil dihapus!"))

@app.route('/toggle_jadwal/<int:id>', methods=['POST'])
@login_required
def toggle_jadwal(id):
    status_baru = request.form.get('status')
    is_active = 1 if status_baru == 'on' else 0
    toggle_schedule(id, is_active)
    status_teks = "diaktifkan" if is_active == 1 else "dinonaktifkan"
    catat_log("sistem", f"Status Jadwal Diubah", f"Jadwal ID {id} {status_teks}.", "System")
    return redirect(url_for('manajemen', pesan=f"Jadwal berhasil {status_teks}!"))

# ===================== LOGS =====================

@app.route('/logs')
@login_required
def logs():
    data_logs = get_all_logs(50)
    tanggal_sekarang = datetime.now().strftime("%d %b %Y")
    return render_template('logs.html', logs=data_logs, hari_ini=tanggal_sekarang)
