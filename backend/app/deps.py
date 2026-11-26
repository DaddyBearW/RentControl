from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
from sqlalchemy.orm import Session
from app.database import get_db
from app.core.config import settings
from app.models import User
security = HTTPBearer(auto_error=False)

def current_user(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)) -> User:
    if not credentials:
        raise HTTPException(401, "Требуется авторизация")
    try:
        payload = jwt.decode(credentials.credentials, settings.secret_key, algorithms=["HS256"])
        user_id = int(payload["sub"])
    except (jwt.InvalidTokenError, KeyError, ValueError):
        raise HTTPException(401, "Недействительный токен")
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(401, "Пользователь не найден")
    return user

def require_roles(*roles):
    def checker(user: User = Depends(current_user)):
        if user.role not in roles:
            raise HTTPException(403, "Недостаточно прав")
        return user
    return checker
