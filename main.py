from fastapi import FastAPI
import sqlite3


app = FastAPI()

def init_db():
    conn   = sqlite3.connect("pplk_tugas.db")
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS maba (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nama TEXT,
            nim INTEGER,
            kelompok INTEGER,
            link_tugas TEXT
        )
    """)
    conn.commit()
    conn.close()

init_db()

@app.get("/")
def home():
    return {"message": "Sistem Back End PPLK 2026 Aktif dengan Database SQLite!"}



@app.get("/tugas")
def lihat_tugas(nim_kamu: int = None):
    status_sekarang = "Belum mengumpulkan"

    conn   = sqlite3.connect("pplk_tugas.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM maba WHERE nim = ?", (nim_kamu,))
    data   = cursor.fetchone()
    conn.close()

    if data:
        status_sekarang = "Gile lu ! jago banget udah ngumpulin"

    return {
    "nama_tugas": "Resume Perkenalan",
    "Deadline": "22 July 2026",
    "status": status_sekarang
}

@app.post("/kumpul")
def kumpul_tugas(nama: str, nim: int, kelompok: int, link_tugas: str):
    conn   = sqlite3.connect("pplk_tugas.db")
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO maba (nama, nim, kelompok, link_tugas)
        VALUES (?, ?, ?, ?)
    """, (nama, nim, kelompok, link_tugas))
    conn.commit()
    conn.close()

    return {
        "status": "Sukses",
        "pesan": f"Halo {nama} ({nim}), tugas kelompok {kelompok} berhasil dikumpulkan ke dalam database SQLite kelompok {kelompok}!"
    }
    

@app.get("/rekap-tugas")
def lihat_semua_tugas():
    conn = sqlite3.connect("pplk_tugas.db")
    # Hasil otomatis jadi format JSON/Dictionary 
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM maba")
    rows = cursor.fetchall()
    conn.close()

    semua_data =[dict(row) for row in rows]

    return {"total_mengumpulkan": len(semua_data), "data": semua_data}

@app.get("/cek-kelompok/{nomor_kelompok}")
def cek_per_kelompok(nomor_kelompok: int):
    conn = sqlite3.connect("pplk_tugas.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM maba WHERE kelompok = ?", (nomor_kelompok,))
    rows = cursor.fetchall()
    conn.close()
    
    hasil_filter =[dict(row) for row in rows]

    return {
        "kelompok": nomor_kelompok,
        "total_anak_yang_ngumpul": len(hasil_filter),
        "daftar_mahasiswa": hasil_filter
    }