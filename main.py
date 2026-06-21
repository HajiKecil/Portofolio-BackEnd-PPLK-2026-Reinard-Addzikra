from fastapi import FastAPI
import sqlite3

# Membuat aplikasi web backend menggunakan FastAPI
app = FastAPI()

def init_db():
    # Membuka file database, kalau ngga ada filenya maka akan otomatis buat baru
    conn   = sqlite3.connect("pplk_tugas.db")
    # Menulis perintah SQL ke database
    cursor = conn.cursor()
    # Perintah membuat tabel maba (lemari arsip) kalau lemarinya belum ada
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS maba (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nama TEXT,
            nim INTEGER,
            kelompok INTEGER,
            link_tugas TEXT
        )
    """)
    # Menyimpan perubahan ke database
    conn.commit()
    # Menutup koneksi ke database
    conn.close()

# Database nya langsung dibuat pas aplikasi pertama kali dinyalakan
init_db()

# =========================================================================
# 1. Menu Home
# =========================================================================
@app.get("/")
def home():
    # Tampilan otomatis saat aplikasi backend nya diakses lewat browser atau aplikasi frontend
    return {"message": "Sistem Back End PPLK 2026 Aktif dengan Database SQLite!"}

# =========================================================================
# 2. Menu Lihat Tugas
# =========================================================================
@app.get("/tugas")
def lihat_tugas(nim_kamu: int = None): # Parameter opsional, kalau ngga dikasih nilai maka default nya None
    status_sekarang = "Belum mengumpulkan"

    conn   = sqlite3.connect("pplk_tugas.db")
    cursor = conn.cursor()

    # Nyari data mahasiswa berdasarkan NIM yang dikasih lewat parameter
    cursor.execute("SELECT * FROM maba WHERE nim = ?", (nim_kamu,))
    # Karena nim itu unik, cukup ambil teratas satu teratas yang ketemu
    data   = cursor.fetchone()
    conn.close()

    # logika kalau data nya ada, maka statusnya "Anda sudah mengumpulkan" 
    if data:
        status_sekarang = "Anda sudah mengumpulkan"

    # Info dan hasil statusnya ditampilkan ke browser
    return {
    "nama_tugas": "Resume Perkenalan",
    "Deadline": "21 Juni 2026",
    "status": status_sekarang
}

# =========================================================================
# 3. Menu Mengumpulkan Tugas
# =========================================================================
@app.post("/kumpul") # <-- menggunakan ".post " karena orang yang mengumpulkan akan memasukkan data, bukan hanya menampilkan tampilan bawaan ".get"
def kumpul_tugas(nama: str, nim: int, kelompok: int, link_tugas: str):
    conn   = sqlite3.connect("pplk_tugas.db")
    cursor = conn.cursor()

    # Memasukkan data yang dikirim baru baru itu ke dalam tabel
    cursor.execute("""
        INSERT INTO maba (nama, nim, kelompok, link_tugas)
        VALUES (?, ?, ?, ?)
    """, (nama, nim, kelompok, link_tugas))
    conn.commit() # Di commit ini biar data orang yang baru mengumpulkan itu ngga hilang
    conn.close()

    return {
        "status": "Sukses",
        "pesan": f"Halo {nama} ({nim}), tugas kelompok {kelompok} berhasil dikumpulkan ke dalam database SQLite kelompok {kelompok}!"
    }
    
# =========================================================================
# 4. Menu Rekap Total
# =========================================================================
@app.get("/rekap-tugas")
def lihat_semua_tugas():
    conn = sqlite3.connect("pplk_tugas.db")

    # Data otomatis dibungkus rapi lengkap dengan judul kolomnya
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Mengambil semua data maba tanpa terkecuali dari database
    cursor.execute("SELECT * FROM maba")
    rows = cursor.fetchall()
    conn.close()

    # Me-looping buat ngubah semua baris data mentah tadi jadi format Dictionary/JSON (JavaScript Object Notation)
    semua_data =[dict(row) for row in rows]

    # Menampilkan total jumlah peserta beserta daftar lengkap datanya
    return {"total_mengumpulkan": len(semua_data), "data": semua_data}

# =========================================================================
# 5. Menu Rekap Per Kelompok (Fitur khusus panitia)
# =========================================================================
@app.get("/cek-kelompok/{nomor_kelompok}")
def cek_per_kelompok(nomor_kelompok: int):
    conn = sqlite3.connect("pplk_tugas.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Mengambil hanya baris mahasiswa yang nomer kelompoknya cocok 
    cursor.execute("SELECT * FROM maba WHERE kelompok = ?", (nomor_kelompok,))
    rows = cursor.fetchall()
    conn.close()
    
    # Dibungkus lagi jadi JSON biar rapi pas dibaca panitia / frontend
    hasil_filter =[dict(row) for row in rows]

    return {
        "kelompok": nomor_kelompok,
        "total_anak_yang_ngumpul": len(hasil_filter),
        "daftar_mahasiswa": hasil_filter
    }

# =========================================================================
# 6. Menu Hapus Tugas (Fitur khusus panitia)
# =========================================================================
@app.delete("/hapus-tugas/{nim_target}")
def hapus_tugas(nim_target: int):
    conn    = sqlite3.connect("pplk_tugas.db")
    cursor  = conn.cursor()

    # Menghapus satu baris peserta yang nim nya cocok dengan target
    cursor.execute("DELETE FROM maba WHERE nim = ?", (nim_target,))

    # 
    conn.commit() # Sama ini juga harus dicommit biar data yang dihapus barusan bener bener ngga ada lagi dari database
    conn.close()

    return {"status": "Sukses", "Pesan": f"Data maba dengan NIM {nim_target} berhasil dihapus!"}

# =========================================================================
# 7. Menu Edit / Update Data Tugas Peserta
# =========================================================================
@app.put("/edit-tugas")
def edit_tugas(nim_kamu: int, nama_baru: str, kelompok_baru: int, link_tugas_baru: str):
    conn    = sqlite3.connect("pplk_tugas.db")
    cursor  = conn.cursor()

    # Perintah update, mengubah isi kolom nama, nim kelompok dan link berdasarkan nim peserta
    cursor.execute("""
        UPDATE maba
        SET nama    = ?, kelompok = ?, link_tugas = ?
        WHERE nim   = ?
    """, (nama_baru, kelompok_baru, link_tugas_baru, nim_kamu))

    conn.commit() # Di save biar hasil editnya tersimpan permanen dan tidak corrupt
    conn.close()

    return {"status": "Sukses", "pesan": f"Data maba dengan NIm {nim_kamu} berhasil diperbarui!"}