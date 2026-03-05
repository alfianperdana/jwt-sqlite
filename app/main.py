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

app = FastAPI(
    title="Training API",
    version="1.0.0",
    description="API interkoneksi data"
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, custom_rate_limit_handler)
app.middleware("http")(audit_log_middleware)

@app.exception_handler(AppError)
async def app_error_handler(request: Request, exc: AppError):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": {
                "code": exc.code,
                "message": exc.message,
                "detail": exc.detail,
            },
            "meta": {
                "path": str(request.url.path),
                "request_id": request.headers.get("X-Request-ID", "")
            },
        },
    )

@app.exception_handler(RequestValidationError)
async def validation_error_handler(request: Request, exc: RequestValidationError):
    detail = []
    for err in exc.errors():
        loc = ".".join([str(x) for x in err.get("loc", []) if x != "body"])
        detail.append({
            "field": loc,
            "issue": err.get("msg", "Validation failed")
        })
    return JSONResponse(
        status_code=422,
        content={
            "success": False,
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "Input tidak valid",
                "detail": detail,
            },
            "meta": {"path": str(request.url.path)},
        },
    )

app.include_router(
    user.router,
    prefix="/v1",
    tags=["users"]
)
app.include_router(auth.router)
app.include_router(audit.router)

@app.get("/")
def root():
    return {"message": "API is running"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}