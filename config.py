# config.py
import os

# Konfigurasi Aplikasi
SECRET_KEY = 'rahasia_super_aman_ini_harus_diganti_nanti'

# Lokasi File Database JSON
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FILES = {
    'mahasiswa': os.path.join(BASE_DIR, 'data.json'),
    'users': os.path.join(BASE_DIR, 'users.json')
}