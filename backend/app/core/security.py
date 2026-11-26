import hashlib, hmac, os
from datetime import datetime, timedelta, timezone
import jwt
from app.core.config import settings
ALGORITHM = "HS256"

def hash_password(password: str) -> str:
    salt = os.urandom(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 240000)
    return salt.hex() + "$" + digest.hex()

def verify_password(password: str, stored: str) -> bool:
    try:
        salt_hex, digest_hex = stored.split("$", 1)
        actual = hashlib.pbkdf2_hmac("sha256", password.encode(), bytes.fromhex(salt_hex), 240000).hex()
        return hmac.compare_digest(actual, digest_hex)
    except (ValueError, TypeError):
        return False

def create_access_token(user_id: int, role: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.access_token_expire_minutes)
    return jwt.encode({"sub": str(user_id), "role": role, "exp": expire}, settings.secret_key, algorithm=ALGORITHM)
