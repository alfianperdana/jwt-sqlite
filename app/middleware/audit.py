import time
from typing import Callable
from fastapi import Request
from jose import jwt
from app.security.jwt import SECRET_KEY, ALGORITHM
from app.database import SessionLocal
from app.models.audit_log import AuditLog

def determine_action(method: str, path: str) -> str:
    if "login" in path: return "LOGIN"
    if method == "POST": return "CREATE"
    if method == "PUT": return "UPDATE"
    if method == "DELETE": return "DELETE"
    return "READ"

def extract_resource(path: str) -> str:
    parts = [p for p in path.split("/") if p and p not in ["v1", "api"]]
    return parts[0] if parts else "unknown"

def extract_resource_id(path: str) -> str:
    parts = path.split("/")
    for p in reversed(parts):
        if p.isdigit():
            return p
    return ""

async def audit_log_middleware(request: Request, call_next: Callable):
    start_time = time.time()
    user_id, username = None, None
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        try:
            token = auth_header.split(" ")[1]
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            user_id = int(payload.get("sub"))
            username = payload.get("username")
        except Exception:
            pass
            
    ip_address = request.client.host
    request_id = request.headers.get("X-Request-ID", f"req_{int(time.time() * 1000)}")
    
    response = await call_next(request)
    duration = time.time() - start_time
    
    action = determine_action(request.method, request.url.path)
    resource = extract_resource(request.url.path)
    
    db = SessionLocal()
    try:
        audit_entry = AuditLog(
            user_id=user_id, username=username or "anonymous",
            ip_address=ip_address, action=action, resource=resource,
            resource_id=extract_resource_id(request.url.path),
            endpoint=request.url.path, method=request.method,
            status_code=response.status_code,
            success="success" if response.status_code < 400 else "error",
            response_summary={"duration_ms": int(duration * 1000)},
            request_id=request_id
        )
        db.add(audit_entry)
        db.commit()
    except Exception as e:
        print(f"Failed to create audit log: {e}")
        db.rollback()
    finally:
        db.close()
        
    response.headers["X-Request-ID"] = request_id
    response.headers["X-Process-Time"] = f"{duration:.4f}s"
    return response
