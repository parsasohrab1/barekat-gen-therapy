import enum
import hashlib
import secrets
from datetime import datetime, timedelta, timezone

import jwt
from passlib.context import CryptContext

from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class Role(str, enum.Enum):
    ADMIN = "admin"
    SCIENTIST = "scientist"
    CLINICIAN = "clinician"
    VIEWER = "viewer"


# Scientist can run research predictions (clinician endpoints) in this platform.
ROLE_HIERARCHY = {
    Role.ADMIN: {Role.ADMIN, Role.SCIENTIST, Role.CLINICIAN, Role.VIEWER},
    Role.SCIENTIST: {Role.SCIENTIST, Role.CLINICIAN, Role.VIEWER},
    Role.CLINICIAN: {Role.CLINICIAN, Role.VIEWER},
    Role.VIEWER: {Role.VIEWER},
}


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


def hash_api_key(api_key: str) -> str:
    return hashlib.sha256(api_key.encode()).hexdigest()


def generate_api_key() -> str:
    return f"bk_{secrets.token_urlsafe(32)}"


def create_access_token(subject: str, role: str, expires_minutes: int | None = None) -> str:
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=expires_minutes or settings.JWT_EXPIRE_MINUTES
    )
    payload = {"sub": subject, "role": role, "exp": expire, "type": "access"}
    return jwt.encode(payload, settings.API_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def decode_access_token(token: str) -> dict:
    return jwt.decode(token, settings.API_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])


def has_role(user_role: Role, required: Role) -> bool:
    return required in ROLE_HIERARCHY.get(user_role, set())
