# 🚀 Training API — Setup Guide

Panduan lengkap untuk menyiapkan dan menjalankan proyek **Training API** berbasis FastAPI dari nol, baik di **macOS** maupun **Windows**.

---

## 📋 Daftar Isi

1. [Prasyarat (Prerequisites)](#1-prasyarat-prerequisites)
2. [Instalasi Python](#2-instalasi-python)
3. [Clone / Download Proyek](#3-clone--download-proyek)
4. [Membuat Virtual Environment](#4-membuat-virtual-environment)
5. [Instalasi Dependensi](#5-instalasi-dependensi)
6. [Struktur Proyek](#6-struktur-proyek)
7. [Menjalankan Server](#7-menjalankan-server)
8. [Verifikasi & Test Endpoint](#8-verifikasi--test-endpoint)
9. [Troubleshooting Umum](#9-troubleshooting-umum)

---

## 1. Prasyarat (Prerequisites)

| Kebutuhan | Versi Minimum | Keterangan |
|-----------|--------------|------------|
| Python | **3.11+** (disarankan 3.13) | Backend runtime |
| pip | bundled dengan Python | Package manager |
| Git | opsional | Untuk clone repo |
| Terminal | zsh / bash (Mac), PowerShell / cmd (Win) | |

> **Tidak perlu** Docker, database, atau Node.js untuk setup ini.

---

## 2. Instalasi Python

### 🍎 macOS

**Cara 1 — Download installer (paling mudah):**
1. Buka [https://www.python.org/downloads/](https://www.python.org/downloads/)
2. Klik **Download Python 3.13.x**
3. Buka file `.pkg` → ikuti wizard instalasi
4. Verifikasi di Terminal:

```bash
python3 --version
# Output: Python 3.13.x
```

**Cara 2 — Homebrew (bagi yang sudah punya Homebrew):**
```bash
brew install python@3.13
```

---

### 🪟 Windows

1. Buka [https://www.python.org/downloads/](https://www.python.org/downloads/)
2. Klik **Download Python 3.13.x**
3. Jalankan installer `.exe`
4. ⚠️ **PENTING:** Centang opsi **"Add Python to PATH"** sebelum klik Install Now
5. Verifikasi di PowerShell / Command Prompt:

```powershell
python --version
# Output: Python 3.13.x
```

---

## 3. Clone / Download Proyek

### Jika menggunakan Git:
```bash
git clone <URL_REPO_KAMU>
# Masuk ke direktori (folder) proyek yang baru saja di-clone
cd tryday4
```

### Jika download manual (ZIP):
1. Download & ekstrak ZIP proyek
2. Buka Terminal / PowerShell
3. Masuk ke direktori (folder) proyek:
```bash
cd /path/ke/tryday4
```

---

## 4. Membuat Virtual Environment

Virtual environment (`.venv`) memastikan dependensi proyek ini terisolasi dan tidak bentrok dengan instalasi Python global.

### 🍎 macOS / Linux
```bash
# Buat venv
python3 -m venv .venv

# Aktifkan
source .venv/bin/activate

# Tanda berhasil: nama venv muncul di prompt
# (.venv) sulaimansaleh@MacBook tryday4 %
```

### 🪟 Windows (PowerShell)
```powershell
# Buat venv
python -m venv .venv

# Aktifkan
.venv\Scripts\Activate.ps1

# Jika muncul error "execution policy":
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
# Lalu coba aktifkan lagi
```

### 🪟 Windows (Command Prompt)
```cmd
python -m venv .venv
.venv\Scripts\activate.bat
```

> 💡 **Setiap kali** membuka terminal baru, kamu harus mengaktifkan venv kembali sebelum menjalankan server.

---

## 5. Instalasi Dependensi

Pastikan venv sudah aktif (ada tanda `(.venv)` di prompt), lalu:

```bash
pip install fastapi uvicorn "pydantic[email]" "python-jose[cryptography]" "passlib[bcrypt]" python-multipart slowapi sqlalchemy
```

Penjelasan masing-masing paket tambahan:

| Paket | Fungsi |
|-------|--------|
| `fastapi` | Framework web API utama |
| `uvicorn` | ASGI server untuk menjalankan FastAPI |
| `pydantic[email]` | Validasi data + dukungan `EmailStr` |
| `python-jose` | Membuat dan memvalidasi JWT (JSON Web Tokens) |
| `passlib[bcrypt]` | Hashing password menggunakan algoritma bcrypt |
| `python-multipart` | Ekstrak form data (standar OAuth2 login API) |
| `slowapi` | Dependensi Rate Limiting di FastAPI |
| `sqlalchemy` | ORM untuk mengatur interaksi database (SQLite) |

> ⚠️ **Khusus zsh (macOS):** gunakan tanda kutip di sekitar `"pydantic[email]"`, `"python-jose[cryptography]"`, dan `"passlib[bcrypt]"`.  
> Tanpa kutip, zsh akan salah menginterpretasi tanda kurung siku.

### Verifikasi instalasi:
```bash
python -c "import fastapi; print(fastapi.__version__)"
# Output: 0.125.0
```

---

## 6. Struktur Proyek

```
tryday4/
├── .venv/                  # Virtual environment (jangan dicommit ke Git)
├── api_security.db         # File SQLite Database lokal
├── app/
│   ├── main.py             # Entry point aplikasi, middleware, exception
│   ├── database.py         # Konfigurasi ORM Database SQLite
│   ├── errors.py           # Custom exception: AppError
│   ├── models/             # ORM Entity Models (User, AuditLog)
│   ├── middleware/         # Custom ASGI middleware (RateLimit, Audit)
│   ├── security/           # Util keamanan (Password hashing, JWT Token)
│   ├── deps/
│   │   └── auth.py         # Dependency: Authentication (Bearer) & RBAC
│   └── routers/
│       ├── auth.py         # Router: /register, /login, dan /me 
│       ├── audit.py        # Router: Endpoint khusus admin /audit-logs
│       └── user.py         # Router: CRUD endpoint user contoh
└── SETUP.md                # File ini
```

### Penjelasan modul baru Hari 4:

- **`app/models`** — Entity mapper table database seperti tabel users dan audittrails. 
- **`app/middleware`** — Pipeline proses request: `rate_limit.py` (Slowapi limiter) dan `audit.py` (Mencatat track record request).
- **`app/security`** — Utilitas kriptografi untuk hashing password (`password.py`) dan menandatangani sesi JWT (`jwt.py`).
- **`app/routers/auth.py`** — Endpoint khusus untuk menerbitkan Token otentikasi.
- **`app/deps/auth.py`** — Dependensi untuk memvalidasi Token JWT aktif (`get_current_user`) beserta layer kontrol wewenang RBAC (`require_roles`).

---

## 7. Menjalankan Server

Pastikan venv aktif, lalu dari root folder proyek:

```bash
uvicorn app.main:app --reload
```

**Output yang diharapkan:**
```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [xxxxx] using WatchFiles
INFO:     Application startup complete.
```

| Flag | Keterangan |
|------|------------|
| `--reload` | Auto-restart server saat ada perubahan file (mode development) |
| `--host 0.0.0.0` | Agar bisa diakses dari perangkat lain di jaringan yang sama |
| `--port 8080` | Ganti port (default: 8000) |

---

## 8. Verifikasi & Test Endpoint

### Buka dokumentasi interaktif (Swagger UI):
```
http://127.0.0.1:8000/docs
```

### Test via curl

**Health check:**
```bash
curl http://127.0.0.1:8000/health
# {"status":"healthy"}
```

**Register User (Create Account):**
```bash
curl -X POST http://127.0.0.1:8080/v1/register \
     -H "Content-Type: application/json" \
     -d '{"username": "admin1", "email": "admin@example.com", "password": "SecurePassword123", "role": "admin"}'
```

**Login (Get Token):**
```bash
curl -X POST http://127.0.0.1:8080/v1/login \
     -H "Content-Type: application/json" \
     -d '{"username": "admin1", "password": "SecurePassword123"}'
     
# Copy "access_token" dari response untuk dipakai di command berikutnya
```

**Get Current User Info (Protected via JWT):**
```bash
curl -H "Authorization: Bearer <TOKEN_DARI_LOGIN>" \
     http://127.0.0.1:8080/v1/me
```

**Testing Rate Limiter (Brute Force Simulation):**
Jalankan command Login secara beruntun 6x dengan cepat (limit 5/menit). Request ke-6 akan mengembalikan HTTP status respon 429 Too Many Requests.

**Check System Audit Logs (RBAC Admin Only):**
```bash
curl -H "Authorization: Bearer <TOKEN_ADMIN_DARI_LOGIN>" \
     http://127.0.0.1:8080/v1/audit-logs
```

---

## 9. Troubleshooting Umum

### ❌ `ImportError: cannot import name 'users' from 'app.routers'`
File router bernama `user.py` (singular), bukan `users.py`. Pastikan import di `main.py` adalah:
```python
from app.routers import user  # ✅ bukan 'users'
```

---

### ❌ `ModuleNotFoundError: No module named 'email_validator'`
Install dengan tanda kutip (penting di zsh):
```bash
pip install "pydantic[email]"
```

---

### ❌ `NameError: name 'Request' is not defined`
Tambahkan `Request` ke import di `main.py`:
```python
from fastapi import FastAPI, Request  # ✅
```

---

### ❌ `IndentationError: expected an indented block`
Python sensitif terhadap indentasi. Gunakan **4 spasi** secara konsisten (aktifkan "Insert Spaces" di editor kamu). Jangan campur tab dan spasi.

---

### ❌ `zsh: no matches found: pydantic[email]`
zsh menginterpretasi `[...]` sebagai glob. Solusinya: selalu bungkus dengan tanda kutip:
```bash
pip install "pydantic[email]"  # ✅
```

---

### ❌ Venv tidak aktif / command not found
Setiap buka terminal baru, aktifkan dulu:
```bash
# macOS/Linux
source .venv/bin/activate

# Windows PowerShell
.venv\Scripts\Activate.ps1
```

---

## ✅ Checklist Cepat

```
[ ] Python 3.11+ terinstall
[ ] Folder proyek sudah di-download / clone
[ ] Virtual environment dibuat: python3 -m venv .venv
[ ] Venv diaktifkan (ada tanda (.venv) di prompt)
[ ] Dependensi terinstall: pip install fastapi uvicorn "pydantic[email]"
[ ] Server berjalan: uvicorn app.main:app --reload
[ ] Swagger UI terbuka di http://127.0.0.1:8000/docs
```
