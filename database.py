import os
import sqlite3
from datetime import datetime
from config import DB_NAME, AUDIO_DIR

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS audio 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, nama_file TEXT, teks TEXT, waktu_dibuat TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS jadwal 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, nama_jadwal TEXT, waktu_putar TEXT, audio_id INTEGER, is_active INTEGER DEFAULT 1)''')
    try:
        c.execute("ALTER TABLE jadwal ADD COLUMN is_active INTEGER DEFAULT 1")
    except:
        pass
    c.execute('''CREATE TABLE IF NOT EXISTS logs 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, kategori TEXT, pesan TEXT, detail TEXT, tanggal TEXT, jam TEXT, status TEXT)''')
    conn.commit()
    conn.close()

def catat_log(kategori, pesan, detail, status):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    sekarang = datetime.now()
    tanggal = sekarang.strftime("%d %b %Y")
    jam = sekarang.strftime("%H:%M")
    c.execute("INSERT INTO logs (kategori, pesan, detail, tanggal, jam, status) VALUES (?, ?, ?, ?, ?, ?)", 
              (kategori, pesan, detail, tanggal, jam, status))
    conn.commit()
    conn.close()

def get_audio_list(only_local=True):
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    if only_local:
        c.execute("SELECT * FROM audio WHERE nama_file NOT LIKE 'http%' ORDER BY id DESC")
    else:
        c.execute("SELECT * FROM audio ORDER BY id DESC")
    rows = c.fetchall()
    conn.close()
    return rows

def get_audio_by_id(audio_id):
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT * FROM audio WHERE id = ?", (audio_id,))
    row = c.fetchone()
    conn.close()
    return row

def insert_audio(nama_file, teks):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("INSERT INTO audio (nama_file, teks, waktu_dibuat) VALUES (?, ?, ?)", 
              (nama_file, teks, datetime.now().strftime("%Y-%m-%d %H:%M")))
    audio_id = c.lastrowid
    conn.commit()
    conn.close()
    return audio_id

def delete_audio(audio_id):
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT nama_file FROM audio WHERE id = ?", (audio_id,))
    audio = c.fetchone()
    nama_file = None
    if audio:
        nama_file = audio['nama_file']
        if not nama_file.startswith('http'):
            path_file = os.path.join(AUDIO_DIR, nama_file)
            if os.path.exists(path_file):
                os.remove(path_file)
        c.execute("DELETE FROM audio WHERE id = ?", (audio_id,))
        c.execute("DELETE FROM jadwal WHERE audio_id = ?", (audio_id,))
    conn.commit()
    conn.close()
    return nama_file

def get_schedules():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute('''SELECT jadwal.id, jadwal.nama_jadwal, jadwal.waktu_putar, audio.teks, jadwal.is_active 
                 FROM jadwal 
                 JOIN audio ON jadwal.audio_id = audio.id 
                 ORDER BY jadwal.waktu_putar ASC''')
    rows = c.fetchall()
    conn.close()
    return rows

def get_active_schedules_by_time(waktu):
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute('''SELECT jadwal.nama_jadwal, audio.nama_file 
                 FROM jadwal 
                 JOIN audio ON jadwal.audio_id = audio.id 
                 WHERE jadwal.waktu_putar = ? AND jadwal.is_active = 1''', (waktu,))
    rows = c.fetchall()
    conn.close()
    return rows

def insert_schedule(nama_jadwal, waktu_putar, audio_id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("INSERT INTO jadwal (nama_jadwal, waktu_putar, audio_id, is_active) VALUES (?, ?, ?, 1)", 
              (nama_jadwal, waktu_putar, audio_id))
    conn.commit()
    conn.close()

def update_schedule(jadwal_id, nama_jadwal, jam):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("UPDATE jadwal SET nama_jadwal=?, waktu_putar=? WHERE id=?", (nama_jadwal, jam, jadwal_id))
    conn.commit()
    conn.close()

def delete_schedule(jadwal_id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("DELETE FROM jadwal WHERE id = ?", (jadwal_id,))
    conn.commit()
    conn.close()

def toggle_schedule(jadwal_id, is_active):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("UPDATE jadwal SET is_active = ? WHERE id = ?", (is_active, jadwal_id))
    conn.commit()
    conn.close()

def get_recent_logs(limit=3):
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT * FROM logs ORDER BY id DESC LIMIT ?", (limit,))
    rows = c.fetchall()
    conn.close()
    return rows

def get_all_logs(limit=50):
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT * FROM logs ORDER BY id DESC LIMIT ?", (limit,))
    rows = c.fetchall()
    conn.close()
    return rows
