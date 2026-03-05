# 🛡️ FastAPI SQLite with JWT, RBAC, Rate Limiting, and Audit Logging

[![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com/)
[![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![SQLite](https://img.shields.io/badge/SQLite-07405E?style=for-the-badge&logo=sqlite&logoColor=white)](https://www.sqlite.org/)

Sebuah proyek pelatihan API backend yang komprehensif menggunakan FastAPI. Proyek ini mendemonstrasikan struktur backend yang solid dan modern, mengimplementasikan Autentikasi (JWT), Kontrol Akses Berbasis Peran (RBAC), Pembatasan Laju (Rate Limiting), Pencatatan Audit (Audit Logging), serta Penanganan Error Khusus (Custom Error Handling) menggunakan basis data SQLite.

---

## 🌟 Fitur Utama

- **🚀 FastAPI Framework**: Kinerja tinggi, sangat cepat, mudah dipelajari, dan siap untuk diproduksi.
- **🗄️ SQLite Database**: Database yang ringan dan berbasis disk dengan ORM `SQLAlchemy`.
- **🔐 Autentikasi & Otorisasi**:
  - Implementasi aman menggunakan JWT (JSON Web Tokens).
  - Role-Based Access Control (RBAC) untuk mengelola izin setiap role pengguna dengan mudah.
- **🛡️ Keamanan & Reliabilitas**:
  - **Rate Limiting**: Melindungi berbagai endpoint dari serangan DDoS maupun *brute-force* menggunakan `slowapi`.
  - **Audit Logging**: Mencatat (log) semua permintaan HTTP (request) untuk memudahkan pengawasan dan perbaikan secara terpusat.
  - **Custom Error Handling**: Response error diseragamkan dengan format JSON untuk error aplikasi dan kegagalan validasi.
- **🧩 Struktur Modular**: Kode terorganisasi dengan baik (`routers`, `models`, `schemas`, `middleware`, `deps`).

---

## 🛠️ Tech Stack

| Teknologi | Deskripsi |
| :--- | :--- |
| **Python 3.x** | Bahasa Pemrograman Utama |
| **FastAPI** | Web Framework |
| **SQLAlchemy** | Object Relational Mapper (ORM) |
| **SQLite** | Basis Data (Sistem Relasional) |
| **PyJWT** | Library Autentikasi JWT |
| **Passlib / Bcrypt** | Hashing Keamanan Kata Sandi |
| **SlowAPI** | Extensi Rate Limiting FastAPI |
| **Uvicorn** | ASGI Server untuk Menjalankan Aplikasi |

---

## 📦 Panduan Instalasi & Menjalankan Aplikasi

Ikuti langkah-langkah di bawah ini untuk mengatur dan menjalankan aplikasi di komputer/server lokal Anda.

### 1. Clone Repositori
```bash
git clone <repository-url>
cd jwt-sqlite
```

### 2. Buat & Aktifkan Virtual Environment
Sangat disarankan memakai Virtual Environment (`.venv`) agar dependensi tidak bertabrakan dengan sistem yang lain.

```bash
# Membuat virtual environment
python -m venv .venv

# Mengaktifkan (Mac/Linux)
source .venv/bin/activate

# Mengaktifkan (Windows)
.venv\Scripts\activate
```

### 3. Instalasi Dependensi
Pastikan Anda sudah menginstal seluruh *package* Python yang dibutuhkan:
```bash
pip install fastapi uvicorn sqlalchemy passlib bcrypt pyjwt slowapi
```

### 4. Mulai Aplikasi
Jalankan server aplikasi FastAPI menggunakan Uvicorn:
```bash
uvicorn app.main:app --reload --port 8000
```

> **Catatan**: Aplikasi akan berjalan di `http://localhost:8000`.

---

## 📖 Dokumentasi API

FastAPI secara otomatis men-*generate* halaman dokumentasi interaktif. Setelah server menyala, Anda bisa mengakses URL berikut:
- **Swagger UI**: [http://localhost:8000/docs](http://localhost:8000/docs) *(Paling direkomendasikan untuk testing)*
- **ReDoc**: [http://localhost:8000/redoc](http://localhost:8000/redoc)

### Ringkasan Endpoint Utama:
- `POST /auth/login` : Autentikasi & Pembuatan Token JWT.
- `GET /v1/users/me` : Mendapatkan profil *user* yang sedang aktif.
- `GET /v1/users/` : Manajemen pengguna (dilindungi berdasarkan peran RBAC).
- `GET /audit/` : Melihat daftar rekam jejak aktivitas (Audit Logs).

---

## 📂 Struktur Folder Proyek

Untuk mempermudah pemahaman alur kerja basis kode:

```text
jwt-sqlite/
├── app/
│   ├── database.py       # Konfigurasi Koneksi & Base SQLAlchemy
│   ├── deps/             # Dependency injection (e.g. get_db, current_user)
│   ├── errors.py         # Exception handling / Error khusus terpusat
│   ├── main.py           # Inisialisasi utama aplikasi FastAPI
│   ├── middleware/       # Custom middleware (Rate Limiting, Audit Log)
│   ├── models/           # Definisi skema tabel pada ORM (User, AuditLog)
│   ├── routers/          # Endpoint API berdasarkan fungsionalitas
│   ├── schemas/          # Validasi tipe data (Request & Response) dengan Pydantic
│   └── security/         # Fungsi helper (hashing password, token JWT)
├── api_security.db       # File database SQLite (ter-generate saat aplikasi diakses)
└── README.md             # Dokumentasi utama proyek
```

---

## 🛡️ Praktik Terbaik (Best Practices) yang Digunakan
1. **Pemisahan Konteks (Separation of Concerns)**: Batas yang jelas antara definisi skema, struktur model *database*, lalu lintas rute, dan injeksi *dependency*.
2. **Middleware Terintegrasi**: Mengintersepsi setiap siklus aliran data, seperti *rate-limiter* dan *audit-logger*, tanpa mengotori setiap *endpoints*.
3. **Standarisasi Respon & Error**: Tidak ada *Internal Server Error* bawaan karena sudah ditangkap oleh `AppError` secara global.
