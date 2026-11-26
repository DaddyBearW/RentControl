from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User
from app.schemas import UserCreate, Login, TokenOut, UserOut
from app.core.security import hash_password, verify_password, create_access_token
from app.deps import current_user
router = APIRouter(prefix="/api/auth", tags=["Авторизация"])

@router.post("/register", response_model=TokenOut, status_code=201)
def register(data: UserCreate, db: Session = Depends(get_db)):
    if db.query(User).filter(User.email == data.email).first():
        raise HTTPException(409, "Пользователь с таким email уже существует")
    user = User(email=data.email, full_name=data.full_name, password_hash=hash_password(data.password), role="customer")
    db.add(user); db.commit(); db.refresh(user)
    return {"access_token": create_access_token(user.id, user.role), "user": user}

@router.post("/login", response_model=TokenOut)
def login(data: Login, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == data.email).first()
    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(401, "Неверный email или пароль")
    return {"access_token": create_access_token(user.id, user.role), "user": user}

@router.get("/me", response_model=UserOut)
def me(user: User = Depends(current_user)):
    return user
