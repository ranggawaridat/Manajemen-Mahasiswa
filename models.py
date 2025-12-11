# models.py

class MahasiswaModel:
    """
    Representasi Data Mahasiswa (OOP).
    """
    def __init__(self, nim, nama, jurusan, email, ipk, id=None):
        self.id = id
        self.nim = nim
        self.nama = nama
        self.jurusan = jurusan
        self.email = email
        self.ipk = float(ipk) if ipk else 0.0

    def to_dict(self):
        """Konversi Object ke Dictionary untuk disimpan ke JSON"""
        return {
            "id": self.id,
            "nim": self.nim,
            "nama": self.nama,
            "jurusan": self.jurusan,
            "email": self.email,
            "ipk": self.ipk
        }