from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from datetime import timedelta
from app.database import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserLogin, UserOut, Token
from app.security.password import hash_password, verify_password
from app.security.jwt import create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES
from app.deps.auth import get_current_user
from app.middleware.rate_limit import limiter

router = APIRouter(prefix="/v1", tags=["Authentication"])

@router.post("/register", status_code=status.HTTP_201_CREATED, response_model=UserOut)
@limiter.limit("10/minute")
def register_user(request: Request, payload: UserCreate, db: Session = Depends(get_db)):
    # Check existing username
    existing = db.query(User).filter(User.username == payload.username).first()
    if existing:
        raise HTTPException(status_code=409, detail="Username already registered")
    
    # Check existing email
    existing_email = db.query(User).filter(User.email == payload.email).first()
    if existing_email:
        raise HTTPException(status_code=409, detail="Email already registered")
        
    # Hash password & create user
    hashed = hash_password(payload.password)
    db_user = User(
        username=payload.username,
        email=payload.email,
        hashed_password=hashed,
        full_name=payload.full_name,
        role=payload.role,
        is_active=True
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@router.post("/login", response_model=Token)
@limiter.limit("5/minute")
def login(request: Request, payload: UserLogin, db: Session = Depends(get_db)):
    # Find user
    user = db.query(User).filter(User.username == payload.username).first()
    # User not found or wrong password
    if not user or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(
            status_code=401, detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"}
        )
        
    # Check active
    if not user.is_active:
        raise HTTPException(status_code=403, detail="User account is inactive")
        
    # Create JWT
    expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id), "username": user.username, "role": user.role},
        expires_delta=expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", response_model=UserOut)
def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Get authenticated user information - Protected endpoint"""
    return current_user
