# 📖 Code Walkthrough — Training API

Penjelasan mendetail **per file** dan **per baris kode** untuk seluruh proyek ini.

---

## Peta File

```
app/
├── main.py          ← Entry point: inisialisasi app, middleware (audit, limitter) & error handler
├── database.py      ← Setup koneksi Engine dan session API SQLAlchemy (SQLite)
├── errors.py        ← Custom exception class (AppError)
├── models/
│   ├── user.py      ← Schema DB User beserta field password_hash JWT
│   └── audit_log.py ← Schema histori akses request pengguna
├── middleware/
│   ├── audit.py     ← Middleware penangkap HTTP Request Who,What,When
│   └── rate_limit.py← Setup SlowAPI Limiter anti brute-force 
├── security/
│   ├── jwt.py       ← Konstruksi dan dekonstruksi session signature JWT 
│   └── password.py  ← Algoritma salting hashing (Bcrypt) passlib
├── deps/
│   └── auth.py      ← Dependency: get_current_user & require_roles (RBAC checker)
└── routers/
    ├── auth.py      ← POST register, login & me
    ├── audit.py     ← GET admin-dashboard audit trail
    └── user.py      ← endpoint CRUD dummy sisanya
```

---

## 1. `app/errors.py`

> **Peran:** Mendefinisikan format error custom yang konsisten di seluruh aplikasi.

```python
class AppError(Exception):           # (1)
    def __init__(                    # (2)
        self,
        status_code: int,            # (3)
        code: str,                   # (4)
        message: str,                # (5)
        detail: list | None = None   # (6)
    ):
        self.status_code = status_code  # (7)
        self.code = code                # (8)
        self.message = message          # (9)
        self.detail = detail or []      # (10)
```

| Baris | Penjelasan |
|-------|-----------|
| **(1)** `class AppError(Exception)` | Membuat class baru yang mewarisi (`extends`) dari `Exception` bawaan Python. Artinya `AppError` adalah sebuah exception yang bisa di-`raise`. |
| **(2)** `def __init__(...)` | Konstruktor class — dijalankan otomatis saat kita menulis `AppError(...)`. |
| **(3)** `status_code: int` | Parameter wajib: HTTP status code yang akan dikirim ke client (misal: 404, 401, 500). Tipe `int` = harus angka. |
| **(4)** `code: str` | Kode error singkat berbentuk string (misal: `"USER_NOT_FOUND"`). Dipakai oleh client untuk logika kondisional. |
| **(5)** `message: str` | Pesan error yang lebih panjang dan ramah dibaca manusia (misal: `"User tidak ditemukan"`). |
| **(6)** `detail: list \| None = None` | Detail tambahan opsional — misal daftar field yang gagal validasi. Default `None` jika tidak diisi. |
| **(7)** `self.status_code = status_code` | Menyimpan nilai `status_code` ke dalam objek supaya bisa diakses dari luar class dengan `exc.status_code`. |
| **(8)** `self.code = code` | Sama — menyimpan kode error ke objek. |
| **(9)** `self.message = message` | Menyimpan pesan error ke objek. |
| **(10)** `self.detail = detail or []` | Jika `detail` bernilai `None` (tidak diisi), gunakan list kosong `[]` sebagai default agar respons selalu konsisten. |

---

## 2. `app/deps/auth.py`

> **Peran:** Dependency yang memvalidasi header `Authorization` dan mengekstrak token Bearer.

> **Peran:** Dependency yang memvalidasi header JWT `Authorization`, mengekstrak claims Bearer, dan melakukan Authorization lapis RBAC.

```python
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError
from sqlalchemy.orm import Session
from app.database import get_db
from app.security.jwt import verify_token
from app.models.user import User
from app.schemas.user import TokenData
from typing import List

security = HTTPBearer()

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    token = credentials.credentials
    try:
        payload = verify_token(token)
        ... # extract user context logic
    except JWTError:
        raise credentials_exception

    user = db.query(User).filter(User.id == token_data.user_id).first()
    return user

def require_roles(allowed_roles: List[str]):
    def role_checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in allowed_roles:
            raise HTTPException(status_code=403, detail="Access forbidden")
        return current_user
    return role_checker
```

| Baris | Penjelasan |
|-------|-----------|
| **(1)** `credentials = Depends(security)` | FastAPI membaca header `Authorization` Bearer dari request via skema standar bawaan `HTTPBearer()`. |
| **(2)** `get_current_user()` | Ini adalah **Dependency Function**. FastAPI memanggil fungsi ini sebagai pre-flight validation terhadap akses JWT dan Active Status account User. |
| **(3)** `def require_roles(...)` | Dependency Factory (Fungsi yang mengembalikan Fungsi), memvalidasi RBAC pada tingkatan User.role (Contoh: `user` vs `admin`). |


---

## 3. `app/main.py`

> **Peran:** Entry point aplikasi — tempat `FastAPI` dibuat, error handler global didaftarkan, dan router dipasang.

```python
from fastapi import FastAPI, Request
from app.routers import user, auth, audit
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from app.errors import AppError
from slowapi.errors import RateLimitExceeded
from app.middleware.rate_limit import limiter, custom_rate_limit_handler
from app.middleware.audit import audit_log_middleware
from app.database import engine, Base
import app.models.user
import app.models.audit_log

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Training API", version="1.0.0")

app.state.limiter = limiter                                       # (1)
app.add_exception_handler(RateLimitExceeded, custom_rate_limit_handler) # (2)
app.middleware("http")(audit_log_middleware)                      # (3)

@app.exception_handler(AppError)
async def app_error_handler(request: Request, exc: AppError):
    ...
```

| Baris | Penjelasan |
|-------|-----------|
| **(1)** `app.state.limiter = limiter` | Memasang referensi modul RateLimiter ke objek global FastAPI (app.state). |
| **(2)** `app.add_exception_handler(RateLimitExceeded)` | Mengaitkan default error RateLimit slowapi ke format parser custom `429 Too Many Requests`. |
| **(3)** `app.middleware("http")(audit_log_middleware)` | Mendaftarkan audit fungsi penangkap request (`middleware/audit.py`) untuk di jalankan secara global tiap ada request. |

| Baris | Penjelasan |
|-------|-----------|
| **(1)** `from fastapi import FastAPI, Request` | Import class utama `FastAPI` untuk membuat app, dan `Request` untuk membaca data dari request HTTP (path, headers, dll). |
| **(2)** `from app.routers import user` | Import modul router dari file `app/routers/user.py`. Nama modul `user` (singular) harus cocok persis dengan nama file. |
| **(3)** `from fastapi.responses import JSONResponse` | Import `JSONResponse` — kelas untuk mengirim respons dengan format JSON dan status code kustom. |
| **(4)** `from fastapi.exceptions import RequestValidationError` | Exception bawaan FastAPI yang otomatis di-raise ketika request body tidak sesuai schema Pydantic. |
| **(5)** `from app.errors import AppError` | Import custom exception yang kita buat di `errors.py`. |
| **(6)** `app = FastAPI(...)` | Membuat instance aplikasi FastAPI. Objek `app` ini yang dijalankan oleh uvicorn. |
| **(7)** `title="Training API"` | Judul yang tampil di halaman `/docs` (Swagger UI). |
| **(8)** `version="1.0.0"` | Versi API yang tampil di docs dan respons. |
| **(9)** `description="API interkoneksi data"` | Deskripsi singkat yang tampil di `/docs`. |
| **(10)** `@app.exception_handler(AppError)` | Decorator yang mendaftarkan fungsi di bawahnya sebagai "penangkap" khusus untuk exception bertipe `AppError`. Setiap kali `raise AppError(...)` dipanggil di mana pun dalam app, fungsi ini yang akan dijalankan. |
| **(11)** `async def app_error_handler(request, exc)` | `request` = objek request yang sedang diproses. `exc` = objek `AppError` yang di-raise (berisi `status_code`, `code`, `message`, dll). |
| **(12)** `return JSONResponse(...)` | Mengembalikan respons JSON dengan format terstandar. |
| **(13)** `status_code=exc.status_code` | Ambil HTTP status code dari objek exception (misal 404, 401). |
| **(14)** `"success": False` | Selalu `False` karena ini adalah respons error. |
| **(15)** `"code": exc.code` | Kode error mesin seperti `"USER_NOT_FOUND"`. |
| **(16)** `"message": exc.message` | Pesan error yang dibaca manusia. |
| **(17)** `"detail": exc.detail` | Detail tambahan (list), bisa berisi field mana yang bermasalah. |
| **(18)** `"path": str(request.url.path)` | Path URL yang diakses client (misal `/v1/users/99`). Berguna untuk debugging. |
| **(19)** `request.headers.get("X-Request-ID", "")` | Baca header `X-Request-ID` dari request (biasanya dikirim API gateway untuk tracing). Jika tidak ada, gunakan string kosong. |
| **(20)** `@app.exception_handler(RequestValidationError)` | Handler khusus untuk error validasi Pydantic — misalnya saat field `email` tidak valid atau field wajib tidak dikirim. |
| **(21)** `detail = []` | Siapkan list kosong untuk menampung daftar field yang bermasalah. |
| **(22)** `for err in exc.errors()` | Loop setiap error validasi. Satu request bisa punya banyak field yang salah sekaligus. |
| **(23)** `loc = ".".join([...] if x != "body")` | `err["loc"]` berisi tuple lokasi field, misal `("body", "email")`. Kita buang kata `"body"` dan gabungkan sisanya dengan titik → hasilnya `"email"`. |
| **(24)** `"field": loc` | Nama field yang bermasalah (misal `"email"`, `"name"`). |
| **(25)** `"issue": err.get("msg", ...)` | Pesan validasi dari Pydantic (misal `"value is not a valid email address"`). |
| **(26)** `status_code=422` | HTTP 422 Unprocessable Entity — status standar untuk error validasi input. |
| **(27)** `"code": "VALIDATION_ERROR"` | Kode error tetap/fixed untuk semua error validasi. |
| **(28)** `app.include_router(...)` | Memasang semua endpoint dari modul `user` ke dalam aplikasi utama. |
| **(29)** `user.router` | Objek `APIRouter` yang didefinisikan di `user.py`. |
| **(30)** `prefix="/v1"` | Semua endpoint di router ini otomatis diawali `/v1`. Jadi `GET /users` menjadi `GET /v1/users`. |
| **(31)** `tags=["users"]` | Grup label di Swagger UI — semua endpoint user akan muncul di bawah grup "users". |
| **(32)** `@app.get("/")` | Endpoint root — biasanya dipakai untuk cek apakah server hidup. |
| **(33)** `@app.get("/health")` | Health check endpoint — dipakai oleh load balancer atau monitoring untuk memverifikasi server sehat. |

---

## 4. `app/routers/user.py`

> **Peran:** Mendefinisikan semua endpoint `/users` beserta schema request/response-nya.

### 4a. Imports & Setup

```python
from fastapi import APIRouter, Depends    # (1)
from app.deps.auth import require_token  # (2)
from pydantic import BaseModel, EmailStr, Field  # (3)
from datetime import datetime            # (4)
from app.errors import AppError          # (5)

router = APIRouter()                     # (6)

_fake_db: list[dict] = [                 # (7)
    {"id": 1, "name": "Alice", "email": "alice@example.com",
     "role": "admin", "created_at": "2024-01-01T00:00:00"},
    {"id": 2, "name": "Bob", "email": "bob@example.com",
     "role": "user",  "created_at": "2024-01-02T00:00:00"},
]
```

| Baris | Penjelasan |
|-------|-----------|
| **(1)** `APIRouter, Depends` | `APIRouter` = objek untuk mendefinisikan sekumpulan endpoint (seperti mini-app). `Depends` = cara menyuntikkan dependency (seperti `require_token`) ke endpoint. |
| **(2)** `from app.deps.auth import require_token` | Import fungsi dependency autentikasi yang kita buat. |
| **(3)** `BaseModel, EmailStr, Field` | `BaseModel` = base class Pydantic untuk mendefinisikan schema. `EmailStr` = tipe email yang divalidasi otomatis. `Field` = untuk menambahkan aturan tambahan (min_length, pattern, dll). |
| **(4)** `from datetime import datetime` | Import tipe `datetime` Python standar — dipakai di schema `UserOut` untuk field `created_at`. |
| **(5)** `from app.errors import AppError` | Import custom exception agar bisa di-raise di endpoint. |
| **(6)** `router = APIRouter()` | Buat instance router. Semua `@router.get(...)` dan `@router.post(...)` di file ini akan terdaftar di sini. |
| **(7)** `_fake_db: list[dict] = [...]` | Database palsu di memori — hanya untuk tujuan latihan. Awalan `_` menandakan ini "private" (konvensi Python). Di produksi ini diganti dengan query ke database sungguhan. |

---

### 4b. Schema Pydantic

```python
class UserCreate(BaseModel):            # (1)
    """Schema untuk request create user (POST)"""
    name: str = Field(                  # (2)
        min_length=1, max_length=100,
        description="Nama lengkap user"
    )
    email: EmailStr = Field(description="Email valid")  # (3)
    role: str = Field(                  # (4)
        default="user",
        pattern="^(admin|user|lecturer)$"
    )

class UserUpdate(BaseModel):            # (5)
    """Schema untuk PATCH - semua field optional"""
    name: str | None = Field(None, min_length=1, max_length=100)  # (6)
    email: EmailStr | None = None       # (7)
    role: str | None = Field(None, pattern="^(admin|user|lecturer)$")

class UserOut(BaseModel):               # (8)
    """Schema untuk response user"""
    id: int
    name: str
    email: EmailStr
    role: str
    created_at: datetime                # (9)

    class Config:                       # (10)
        from_attributes = True
```

| Baris | Penjelasan |
|-------|-----------|
| **(1)** `class UserCreate(BaseModel)` | Schema untuk request **membuat** user baru. Pydantic akan otomatis memvalidasi setiap field sesuai aturan yang didefinisikan. |
| **(2)** `name: str = Field(min_length=1, max_length=100)` | Field `name` bertipe string, wajib diisi (`min_length=1`), maksimal 100 karakter. Jika dilanggar → error 422 otomatis. |
| **(3)** `email: EmailStr` | Pydantic akan memvalidasi bahwa nilai adalah email yang valid secara format (misal `abc@def.com`). Butuh package `email-validator`. |
| **(4)** `role: str = Field(default="user", pattern="^(admin\|user\|lecturer)$")` | `default="user"` → kalau tidak dikirim, nilainya `"user"`. `pattern` adalah regex yang membatasi pilihan hanya 3 nilai valid. |
| **(5)** `class UserUpdate(BaseModel)` | Schema untuk **update parsial** (PATCH). Semua field opsional — client bisa mengirim hanya field yang ingin diubah. |
| **(6)** `name: str \| None = Field(None, ...)` | Tipe `str | None` artinya bisa string atau `None`. Default `None` artinya boleh tidak dikirim. |
| **(7)** `email: EmailStr \| None = None` | Email opsional — jika tidak dikirim, nilainya `None` (tidak diubah). |
| **(8)** `class UserOut(BaseModel)` | Schema untuk **output/response** — data yang dikirimkan ke client. FastAPI menyaring field berdasarkan schema ini (field yang tidak ada di sini tidak akan tampil). |
| **(9)** `created_at: datetime` | Pydantic otomatis mengkonversi string ISO seperti `"2024-01-01T00:00:00"` menjadi objek `datetime` Python. |
| **(10)** `class Config: from_attributes = True` | Membolehkan `UserOut` membaca data dari ORM object (seperti SQLAlchemy model) — tidak hanya dari dict. |

---

### 4c. Endpoint-endpoint

```python
@router.get("/users/me")                              # (1)
def get_current_user(auth=Depends(require_token)):    # (2)
    return {
        "success": True,
        "data": {
            "user_id": auth["user_id"],               # (3)
            "token": auth["token"][:10] + "..."       # (4)
        }
    }

@router.get("/users")                                 # (5)
def list_users():
    return {
        "success": True,
        "data": [],                                   # (6)
        "meta": {
            "page": 1,
            "page_size": 20,
            "total_items": 0
        }
    }

@router.get("/users/{user_id}", response_model=UserOut)  # (7)
def get_user(user_id: int):                              # (8)
    user = next(                                         # (9)
        (u for u in _fake_db if u["id"] == user_id),
        None
    )
    if not user:                                         # (10)
        raise AppError(
            status_code=404,
            code="USER_NOT_FOUND",
            message=f"User dengan ID {user_id} tidak ditemukan",
            detail=[]
        )
    return user                                          # (11)
```

| Baris | Penjelasan |
|-------|-----------|
| **(1)** `@router.get("/users/me")` | Mendaftarkan endpoint `GET /v1/users/me` (prefix `/v1` ditambah oleh `main.py`). ⚠️ Harus ditulis **di atas** `/users/{user_id}` — karena jika di bawah, FastAPI akan salah mengira `"me"` adalah sebuah `user_id`. |
| **(2)** `auth=Depends(require_token)` | FastAPI akan menjalankan fungsi `require_token` terlebih dahulu. Hasilnya (dict berisi `token` dan `user_id`) langsung masuk ke parameter `auth`. Jika token tidak valid, request berhenti di sini. |
| **(3)** `auth["user_id"]` | Ambil `user_id` dari hasil yang dikembalikan `require_token` (saat ini nilai dummy `123`). |
| **(4)** `auth["token"][:10] + "..."` | Tampilkan hanya 10 karakter pertama dari token — untuk keamanan, token tidak boleh dikembalikan utuh ke client. |
| **(5)** `@router.get("/users")` | Endpoint untuk mendapatkan **daftar** seluruh user. |
| **(6)** `"data": []` | Masih list kosong — di produksi ini diisi dari query database dengan pagination. |
| **(7)** `@router.get("/users/{user_id}", response_model=UserOut)` | `{user_id}` adalah **path parameter** — nilainya diambil langsung dari URL. `response_model=UserOut` membuat FastAPI otomatis memfilter dan memvalidasi output sesuai schema `UserOut`. |
| **(8)** `def get_user(user_id: int)` | FastAPI otomatis mengkonversi path parameter `user_id` dari string (URL selalu string) menjadi `int`. Jika dikirim bukan angka → error 422 otomatis. |
| **(9)** `user = next((u for u in _fake_db if ...), None)` | Cari user di `_fake_db` yang `id`-nya cocok. `next(..., None)` artinya: ambil item pertama yang ditemukan, atau return `None` jika tidak ada. |
| **(10)** `if not user: raise AppError(...)` | Jika tidak ditemukan (user = `None`), lempar `AppError` yang akan ditangkap oleh `app_error_handler` di `main.py` dan dikembalikan sebagai respons JSON 404. |
| **(11)** `return user` | Kembalikan dict user. FastAPI akan memproses ini melalui `response_model=UserOut` untuk memastikan format output sesuai schema. |

---

## Alur Request Lengkap

```
Client
  │
  │  GET /v1/users/99
  ▼
uvicorn (ASGI server)
  │
  ▼
FastAPI app (main.py)
  │
  ├─► Cocokkan route → ditemukan: get_user(user_id=99)
  │
  ├─► Jalankan Depends → require_token() ← (jika endpoint pakai auth)
  │       └─► Cek header Authorization
  │
  ├─► Jalankan get_user(user_id=99)
  │       └─► Cari di _fake_db → tidak ada
  │       └─► raise AppError(404, "USER_NOT_FOUND", ...)
  │
  ├─► app_error_handler menangkap AppError
  │       └─► Return JSONResponse(status=404, content={...})
  │
  ▼
Client menerima:
{
  "success": false,
  "error": {
    "code": "USER_NOT_FOUND",
    "message": "User dengan ID 99 tidak ditemukan",
    "detail": []
  },
  "meta": { "path": "/v1/users/99", "request_id": "" }
}
```
