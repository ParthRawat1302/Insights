from datetime import datetime, timedelta
from typing import Optional

from jose import jwt, JWTError
from passlib.context import CryptContext

from app.core.config import settings

pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)

MAX_BCRYPT_BYTES = 72

def _normalize_password(password: str) -> str:
    if not password:
        return password

    pwd_bytes = password.encode("utf-8")

    if len(pwd_bytes) > MAX_BCRYPT_BYTES:
        pwd_bytes = pwd_bytes[:MAX_BCRYPT_BYTES]

    return pwd_bytes.decode("utf-8", errors="ignore")

def hash_password(password: str) -> str:
    password = _normalize_password(password)
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    plain_password = _normalize_password(plain_password)
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(
    subject: str,
    expires_delta: Optional[timedelta] = None
) -> str:
    if expires_delta is None:
        expires_delta = timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )

    expire = datetime.utcnow() + expires_delta

    payload = {
        "sub": subject,
        "exp": expire
    }

    return jwt.encode(
        payload,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM
    )

def decode_access_token(token: str) -> Optional[str]:
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM]
        )
        return payload.get("sub")
    except JWTError:
        return None
