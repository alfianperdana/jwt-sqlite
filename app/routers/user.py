from fastapi import APIRouter, Depends, HTTPException
from app.deps.auth import require_roles
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from app.errors import AppError
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User

router = APIRouter()

# In-memory data store
_fake_db: list[dict] = [
    {"id": 1, "name": "Alice", "email": "alice@example.com", "role": "admin", "created_at": "2024-01-01T00:00:00"},
    {"id": 2, "name": "Bob",   "email": "bob@example.com",   "role": "user",  "created_at": "2024-01-02T00:00:00"},
]

class UserCreate(BaseModel):
    """Schema untuk request create user (POST)"""
    name: str = Field(
        min_length=1, max_length=100,
        description="Nama lengkap user"
    )
    email: EmailStr = Field(description="Email valid")
    role: str = Field(
        default="user",
        pattern="^(admin|user|lecturer)$"
    )

class UserUpdate(BaseModel):
    """Schema untuk PATCH - semua field optional"""
    name: str | None = Field(None, min_length=1, max_length=100)
    email: EmailStr | None = None
    role: str | None = Field(None, pattern="^(admin|user|lecturer)$")

class UserOut(BaseModel):
    """Schema untuk response user"""
    id: int
    name: str
    email: EmailStr
    role: str
    created_at: datetime

    class Config:
        from_attributes = True  # Allow ORM models




@router.get("/users")
def list_users():
    return {
        "success": True,
        "data": [],
        "meta": {
            "page": 1,
            "page_size": 20,
            "total_items": 0
        }
    }

# @router.get("/users/{user_id}")
# def get_user(user_id: int):
#     return {
#         "success": True,
#         "data": {
#             "id": user_id,
#             "name": "Sample User",
#             "email": "user@example.com"
#         }
#     }

@router.get("/users/{user_id}", response_model=UserOut)
def get_user(user_id: int):
    user = next((u for u in _fake_db if u["id"] == user_id), None)
    if not user:
        raise AppError(
            status_code=404,
            code="USER_NOT_FOUND",
            message=f"User dengan ID {user_id} tidak ditemukan",
            detail=[]
        )
    return user

@router.delete("/users/{user_id}", status_code=204, dependencies=[Depends(require_roles(["admin"]))])
def delete_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(user)
    db.commit()

