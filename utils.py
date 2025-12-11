import json
import os
import re
from functools import wraps
from flask import session, flash, redirect, url_for
from fpdf import FPDF
from datetime import datetime

# --- JSON IO & VALIDASI (TETAP SAMA) ---
def load_json(filename):
    if not os.path.exists(filename): return []
    try:
        with open(filename, 'r') as file: return json.load(file)
    except: return []

def save_json(filename, data):
    try:
        with open(filename, 'w') as file: json.dump(data, file, indent=4)
    except: pass

def validasi_input(nim, email):
    if not re.match(r'^[0-9]+$', nim): return False, "NIM harus angka!"
    # Regex email sederhana
    if not re.match(r'[^@]+@[^@]+\.[^@]+', email): return False, "Email tidak valid!"
    return True, ""

def butuh_login(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_aktif' not in session:
            flash('Silakan login terlebih dahulu!', 'error')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# --- CLASS PDF CUSTOM (DESAIN UNPAM) ---
class LaporanPDF(FPDF):
    def header(self):
        

        # 4. JUDUL HALAMAN
        self.set_font('Arial', 'B', 14)
        self.cell(0, 10, 'LAPORAN DATA MAHASISWA', 0, 1, 'C')
        self.ln(2)

        # 5. HEADER TABEL (Dipindah ke Header agar muncul di tiap halaman)
        self.set_font('Arial', 'B', 9)
        self.set_fill_color(255, 255, 255) # Putih Polos (Sesuai contoh)
        
        # Kolom: No, NIM, Nama, Jurusan, Email, IPK
        self.cell(10, 8, 'No', 1, 0, 'C', True)
        self.cell(30, 8, 'NIM', 1, 0, 'C', True)
        self.cell(60, 8, 'Nama Mahasiswa', 1, 0, 'C', True)
        self.cell(40, 8, 'Jurusan', 1, 0, 'C', True)
        self.cell(35, 8, 'Email', 1, 0, 'C', True)
        self.cell(15, 8, 'IPK', 1, 1, 'C', True)

    

    