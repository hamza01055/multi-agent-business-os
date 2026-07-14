from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError
from passlib.context import CryptContext
from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
ALGO = "HS256"


def hash_password(p: str) -> str:
    return pwd_context.hash(p)


def verify_password(p: str, hashed: str) -> bool:
    return pwd_context.verify(p, hashed)


def _token(sub: str, ttl: timedelta, kind: str) -> str:
    payload = {"sub": sub, "type": kind, "exp": datetime.now(timezone.utc) + ttl}
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=ALGO)


def create_access_token(user_id: str) -> str:
    return _token(user_id, timedelta(minutes=settings.ACCESS_TOKEN_MINUTES), "access")


def create_refresh_token(user_id: str) -> str:
    return _token(user_id, timedelta(days=settings.REFRESH_TOKEN_DAYS), "refresh")


def decode_token(token: str, expect: str = "access") -> str | None:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGO])
        if payload.get("type") != expect:
            return None
        return payload.get("sub")
    except JWTError:
        return None
