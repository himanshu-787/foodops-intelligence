from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from sqlalchemy import select
from sqlalchemy.orm import Session

from app import models
from app.database import get_db

from app.schemas import Token, UserCreate, UserPublic
from app.security import (
    create_access_token,
    decode_access_token,
    hash_password,
    verify_password,
)

router = APIRouter(prefix="/auth", tags=["auth"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

# Fake storage: email -> hashed password (Phase 5 mein database)
users: dict[str, str] = {}

@router.post("/register", response_model=UserPublic, status_code=201)
def register(user: UserCreate, db: Session = Depends(get_db)):
    existing = db.scalar(select(models.User).where(models.User.email == user.email))
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    db.add(models.User(email=user.email, hashed_password=hash_password(user.password)))
    db.commit()
    return {"email": user.email}


@router.post("/login", response_model=Token)
def login(form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.scalar(select(models.User).where(models.User.email == form.username))
    if not user or not verify_password(form.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    return {"access_token": create_access_token(form.username)}


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> str:
    email = decode_access_token(token)
    user = db.scalar(select(models.User).where(models.User.email == email)) if email else None
    if user is None:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    return user.email

@router.get("/me", response_model=UserPublic)
def me(current_user: str = Depends(get_current_user)):
    return {"email": current_user}