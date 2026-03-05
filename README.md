# FastAPI SQLite with JWT, RBAC, Rate Limiting, and Audit Logging

A complete FastAPI training project showcasing a robust backend structure. This project includes Authentication (JWT), Role-Based Access Control (RBAC), API Rate Limiting, Audit Logging, and custom Error Handling using SQLite as the database.

## 🚀 Features

* **FastAPI Framework**: High performance, easy to learn, fast to code, ready for production.
* **SQLite Database**: Lightweight disk-based database via `SQLAlchemy` ORM.
* **Authentication & Authorization**:
  * JWT (JSON Web Tokens) for secure authentication.
  * Role-Based Access Control (RBAC) to manage user permissions.
* **Security & Reliability**:
  * **Rate Limiting**: Protects endpoints from DDoS or brute-force attacks using `slowapi`.
  * **Audit Logging**: Tracks and logs requests for monitoring and debugging via custom middleware.
  * **Custom Error Handling**: Standardized JSON responses for application and validation errors.
* **Modular Structure**: Organized codebase (routers, models, schemas, middleware, core/deps).

## 🛠️ Tech Stack

* **Python 3.x**
* **FastAPI**
* **SQLAlchemy** (ORM)
* **SQLite** (Database)
* **PyJWT** (Authentication)
* **Passlib** (Password Hashing)
* **SlowAPI** (Rate Limiting)
* **Uvicorn** (ASGI Server)

## 📦 Installation & Setup

Follow these steps to set up and run the project locally.

### 1. Clone the repository
\`\`\`bash
git clone <repository-url>
cd jwt-sqlite
\`\`\`

### 2. Create and Activate Virtual Environment
It is recommended to use a virtual environment to manage dependencies.
\`\`\`bash
# Create virtual environment
python -m venv .venv

# Activate virtual environment
# On macOS/Linux:
source .venv/bin/activate
# On Windows:
.venv\\Scripts\\activate
\`\`\`

### 3. Install Dependencies
Ensure you have all the required Python packages installed.
*(Note: If a `requirements.txt` is not provided, you may need to install standard FastAPI dependencies manually)*
\`\`\`bash
pip install fastapi uvicorn sqlalchemy passlib bcrypt pyjwt slowapi
\`\`\`

### 4. Run the Application
Start the FastAPI server using Uvicorn.
\`\`\`bash
uvicorn app.main:app --reload --port 8000
\`\`\`

The API will be accessible at:
* **Base URL**: \`http://localhost:8000\`
* **Interactive API Docs (Swagger UI)**: \`http://localhost:8000/docs\`
* **Alternative API Docs (ReDoc)**: \`http://localhost:8000/redoc\`

## 📂 Project Structure

\`\`\`text
jwt-sqlite/
├── app/
│   ├── database.py       # Database connection & SQLAlchemy Base
│   ├── deps/             # Dependency injection (e.g., get_db, auth_user)
│   ├── errors.py         # Custom application exceptions
│   ├── main.py           # FastAPI application instance & config
│   ├── middleware/       # Custom middleware (Rate Limiting, Audit Log)
│   ├── models/           # SQLAlchemy database models (User, AuditLog, etc.)
│   ├── routers/          # API endpoints (Auth, User, Audit, dll)
│   ├── schemas/          # Pydantic models for request/response validation
│   └── security/         # Authentication logic (Hashing, JWT creation/verification)
├── api_security.db       # SQLite Database File
└── README.md             # Project documentation (this file)
\`\`\`

## 📝 API Endpoints Summary

Once the application is running, check \`http://localhost:8000/docs\` for full details. The main routers included are:
* **/auth**: Login, token generation.
* **/v1/users**: User management, registration, profile retrieval (protected via RBAC).
* **/audit**: Accessing recorded audit logs.

## 🛡️ Best Practices Implemented
* **Separation of Concerns**: Clear boundary between routes, database models, and busines logic.
* **Middleware Integration**: Intercepting requests for rate limiting and logging before they hit the endpoints.
* **Centralized Exception Handling**: Catching and formatting errors uniformly across the application.
