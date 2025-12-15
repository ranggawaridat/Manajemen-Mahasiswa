from flask import Flask, render_template, request, redirect, url_for, session, flash, make_response
from werkzeug.security import generate_password_hash, check_password_hash
import json
import time
import random
from config import SECRET_KEY, FILES
from models import MahasiswaModel
from utils import load_json, save_json, validasi_input, butuh_login, LaporanPDF
# Import semua algoritma dari file algorithms.py
from algorithms import (
    algo_bubble_sort, algo_selection_sort, algo_insertion_sort, 
    algo_shell_sort, algo_merge_sort, 
    algo_linear_search, algo_sequential_search, algo_binary_search
)

app = Flask(__name__)
app.secret_key = SECRET_KEY

# ==========================================
# ROUTES AUTHENTICATION
# ==========================================
# --- ROUTES AUTH (LOGIN & REGISTER) ---

@app.route('/register', methods=['GET', 'POST'])
def register():
    try:
        if request.method == 'POST':
            users = load_json(FILES['users'])
            # Cek Username
            if any(u['username'] == request.form['username'] for u in users):
                flash('Username sudah digunakan!', 'error')
                # Jika error, render ulang auth.html tapi paksa buka panel register
                return render_template('auth.html', active_page='register')
            
            # Simpan User
            users.append({'username': request.form['username'], 'password': generate_password_hash(request.form['password'])})
            save_json(FILES['users'], users)
            
            flash('Pendaftaran berhasil! Silakan login.', 'success')
            return redirect(url_for('login')) # Setelah sukses daftar, lempar ke login
            
        # Jika GET (Buka halaman), tampilkan auth.html dengan panel register aktif
        return render_template('auth.html', active_page='register')
        
    except Exception as e: return f"Error: {e}"

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        users = load_json(FILES['users'])
        user = next((u for u in users if u['username'] == request.form['username']), None)
        
        if user and check_password_hash(user['password'], request.form['password']):
            session['user_aktif'] = user['username']
            return redirect(url_for('root'))
        
        flash('Username atau password salah!', 'error')
        # Jika login gagal, tetap di halaman auth, panel login aktif
        return render_template('auth.html', active_page='login')
            
    # Jika GET (Buka halaman), tampilkan auth.html dengan panel login aktif
    return render_template('auth.html', active_page='login')

@app.route('/logout')
def logout():
    session.pop('user_aktif', None); return redirect(url_for('login'))

# ==========================================
# ROUTES DASHBOARD & UTAMA
# ==========================================
@app.route('/')
@butuh_login
def root(): return redirect(url_for('dashboard'))

@app.route('/dashboard')
@butuh_login
def dashboard():
    mahasiswa = load_json(FILES['mahasiswa'])
    stats = {}
    for m in mahasiswa: stats[m['jurusan']] = stats.get(m['jurusan'], 0) + 1
    return render_template('dashboard.html', user=session['user_aktif'], total=len(mahasiswa), stats=stats)

@app.route('/mahasiswa')
@butuh_login
def data_mahasiswa():
    mahasiswa = load_json(FILES['mahasiswa'])
    q = request.args.get('q'); algo = request.args.get('algo')
    sort_algo = request.args.get('sort_algo'); sort_by = request.args.get('sort_by', 'ipk')
    
    data = mahasiswa; pesan = None
    
    # 1. Searching Logic (Panggil fungsi dari algorithms.py)
    if q:
        if algo == 'binary': data = algo_binary_search(mahasiswa, q); pesan = f"Cari '{q}' (Binary)"
        elif algo == 'sequential': data = algo_sequential_search(mahasiswa, q); pesan = f"Cari '{q}' (Sequential)"
        else: data = algo_linear_search(mahasiswa, q); pesan = f"Cari '{q}' (Linear)"
        
    # 2. Sorting Logic (Panggil fungsi dari algorithms.py)
    if sort_algo:
        if sort_algo == 'bubble': data = algo_bubble_sort(data, sort_by)
        elif sort_algo == 'selection': data = algo_selection_sort(data, sort_by)
        elif sort_algo == 'insertion': data = algo_insertion_sort(data, sort_by)
        elif sort_algo == 'shell': data = algo_shell_sort(data, sort_by)
        elif sort_algo == 'merge': data = algo_merge_sort(data, sort_by)
        pesan = (pesan + " | " if pesan else "") + f"Sort {sort_by} via {sort_algo}"

    return render_template('index.html', mahasiswa=data, user=session['user_aktif'], query=q, algo=algo, sort_algo=sort_algo, sort_by=sort_by, pesan=pesan)

# ==========================================
# ROUTES CRUD (Create, Update, Delete)
# ==========================================
@app.route('/tambah', methods=['POST'])
@butuh_login
def tambah():
    valid, msg = validasi_input(request.form['nim'], request.form['email'])
    if not valid: return f"<script>alert('{msg}'); window.history.back();</script>"
    
    data = load_json(FILES['mahasiswa'])
    new_id = (data[-1]['id'] + 1) if data else 1
    # Menggunakan Class MahasiswaModel dari models.py
    mhs = MahasiswaModel(request.form['nim'], request.form['nama'], request.form['jurusan'], request.form['email'], request.form['ipk'], new_id)
    data.append(mhs.to_dict())
    save_json(FILES['mahasiswa'], data)
    return redirect(url_for('data_mahasiswa'))

@app.route('/edit/<int:id>', methods=['GET', 'POST'])
@butuh_login
def edit(id):
    data = load_json(FILES['mahasiswa'])
    mhs = next((i for i in data if i["id"] == id), None)
    if not mhs: return "Not Found", 404
    if request.method == 'POST':
        valid, msg = validasi_input(request.form['nim'], request.form['email'])
        if not valid: return f"<script>alert('{msg}'); window.history.back();</script>"
        mhs.update({"nim": request.form['nim'], "nama": request.form['nama'], "jurusan": request.form['jurusan'], "email": request.form['email'], "ipk": request.form['ipk']})
        save_json(FILES['mahasiswa'], data); return redirect(url_for('data_mahasiswa'))
    return render_template('edit.html', mahasiswa=mhs, user=session['user_aktif'])

@app.route('/hapus/<int:id>')
@butuh_login
def hapus(id):
    data = load_json(FILES['mahasiswa'])
    save_json(FILES['mahasiswa'], [i for i in data if i['id'] != id])
    return redirect(url_for('data_mahasiswa'))

# ==========================================
# ROUTES LAIN (PDF & BENCHMARK)
# ==========================================
@app.route('/cetak-pdf')
@butuh_login
def cetak_pdf():
    # 1. Ambil DATA
    mahasiswa = load_json(FILES['mahasiswa'])
    
    # 2. Siapkan PDF
    pdf = LaporanPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    
    # 3. Isi Tabel
    pdf.set_font('Arial', '', 8) # Font isi 8 agar muat
    
    no = 1
    for mhs in mahasiswa:
        # Ambil data aman (hindari error jika kosong)
        nim = str(mhs.get('nim', '-'))
        nama = mhs.get('nama', '-').upper()
        jurusan = mhs.get('jurusan', '-')
        email = mhs.get('email', '-')
        ipk = str(mhs.get('ipk', '0.00'))

        # --- CETAK BARIS (Angka Lebar HARUS SAMA dengan utils.py) ---
        
        # No (Lebar 10)
        pdf.cell(10, 8, str(no), 1, 0, 'C')
        
        # NIM (Lebar 30)
        pdf.cell(30, 8, nim, 1, 0, 'C')
        
        # Nama (Lebar 60) - Potong jika kepanjangan (>30 huruf)
        pdf.cell(60, 8, nama[:30], 1, 0, 'L') 
        
        # Jurusan (Lebar 40) - Potong jika kepanjangan (>20 huruf)
        pdf.cell(40, 8, jurusan[:20], 1, 0, 'L')
        
        # Email (Lebar 35) - Potong jika kepanjangan (>20 huruf)
        pdf.cell(35, 8, email[:20], 1, 0, 'L')
        
        # IPK (Lebar 15)
        pdf.cell(15, 8, ipk, 1, 1, 'C') # Parameter terakhir 1 (Pindah Baris)
        
        no += 1


    # 5. Output
    response = make_response(pdf.output(dest='S').encode('latin-1'))
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'attachment; filename=Laporan_Data_Mahasiswa.pdf'
    return response

@app.route('/benchmark')
@butuh_login
def benchmark():
    return render_template('benchmark.html', user=session['user_aktif'])

@app.route('/run-benchmark')
@butuh_login
def run_benchmark():
    # Ambil data asli untuk disimulasikan
    real_data = load_json(FILES['mahasiswa'])
    if not real_data: real_data = [{'ipk': 3.0, 'nama': 'Dummy'}] 

    sizes = [50, 100, 200, 500]
    results = {'labels': sizes, 'bubble': [], 'selection': [], 'insertion': [], 'shell': [], 'merge': []}
    
    for n in sizes:
        test_data = []
        while len(test_data) < n: test_data.extend(real_data)
        test_data = test_data[:n]
        
        # Jalankan test menggunakan algoritma yang di-import
        start = time.perf_counter(); algo_bubble_sort(test_data.copy(), 'ipk'); results['bubble'].append(round((time.perf_counter()-start)*1000, 2))
        start = time.perf_counter(); algo_selection_sort(test_data.copy(), 'ipk'); results['selection'].append(round((time.perf_counter()-start)*1000, 2))
        start = time.perf_counter(); algo_insertion_sort(test_data.copy(), 'ipk'); results['insertion'].append(round((time.perf_counter()-start)*1000, 2))
        start = time.perf_counter(); algo_shell_sort(test_data.copy(), 'ipk'); results['shell'].append(round((time.perf_counter()-start)*1000, 2))
        start = time.perf_counter(); algo_merge_sort(test_data.copy(), 'ipk'); results['merge'].append(round((time.perf_counter()-start)*1000, 2))
        
    return json.dumps(results)

if __name__ == '__main__':
    app.run(debug=True) 