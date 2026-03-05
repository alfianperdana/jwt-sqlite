from slowapi import Limiter
from fastapi import Request
from jose import jwt, JWTError
from app.security.jwt import SECRET_KEY, ALGORITHM
from fastapi.responses import JSONResponse
from slowapi.errors import RateLimitExceeded

def get_user_identifier(request: Request) -> str:
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header.split(" ")[1]
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            user_id = payload.get("sub")
            if user_id:
                return f"user:{user_id}"
        except JWTError:
            pass
    return f"ip:{request.client.host}"

limiter = Limiter(
    key_func=get_user_identifier,
    default_limits=["100/minute"]
)

def custom_rate_limit_handler(request: Request, exc: RateLimitExceeded) -> JSONResponse:
    retry_after = 60
    if "Retry after" in str(exc.detail):
        try:
            retry_after = int(str(exc.detail).split("Retry after ")[1].split(" ")[0])
        except (IndexError, ValueError):
            pass
            
    return JSONResponse(
        status_code=429,
        content={
            "success": False,
            "error": {
                "code": "RATE_LIMIT_EXCEEDED",
                "message": "Too many requests. Please try again later.",
                "detail": f"Retry after {retry_after} seconds"
            }
        },
        headers={
            "Retry-After": str(retry_after),
            "X-RateLimit-Remaining": "0"
        }
    )
