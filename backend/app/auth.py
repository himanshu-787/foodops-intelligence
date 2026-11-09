from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

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
def register(user: UserCreate):
    if user.email in users:
        raise HTTPException(status_code=400, detail="Email already registered")
    users[user.email] = hash_password(user.password)
    return {"email": user.email}


@router.post("/login", response_model=Token)
def login(form: OAuth2PasswordRequestForm = Depends()):
    hashed = users.get(form.username)
    if not hashed or not verify_password(form.password, hashed):
        # Dono case mein same message: attacker ko pata na chale email exist karta hai
        raise HTTPException(status_code=401, detail="Invalid email or password")
    return {"access_token": create_access_token(form.username)}


def get_current_user(token: str = Depends(oauth2_scheme)) -> str:
    email = decode_access_token(token)
    if email is None or email not in users:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    return email


@router.get("/me", response_model=UserPublic)
def me(current_user: str = Depends(get_current_user)):
    return {"email": current_user}