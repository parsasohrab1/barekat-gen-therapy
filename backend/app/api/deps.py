import uuid
from dataclasses import dataclass

from fastapi import Depends, HTTPException, status
from fastapi.security import APIKeyHeader, HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import SessionLocal
from app.core.security import Role, decode_access_token, has_role, hash_api_key
from app.models import User

bearer_scheme = HTTPBearer(auto_error=False)
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


@dataclass
class CurrentUser:
    id: uuid.UUID | None
    username: str
    role: Role


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_user(
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    api_key: str | None = Depends(api_key_header),
) -> CurrentUser:
    if not settings.AUTH_ENABLED:
        return CurrentUser(id=None, username="anonymous", role=Role.SCIENTIST)

    if api_key:
        key_hash = hash_api_key(api_key)
        user = db.scalars(
            select(User).where(User.api_key_hash == key_hash, User.is_active.is_(True))
        ).first()
        if user:
            return CurrentUser(id=user.id, username=user.username, role=Role(user.role))
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid API key")

    if credentials:
        try:
            payload = decode_access_token(credentials.credentials)
            username = payload.get("sub")
            user = db.scalars(
                select(User).where(User.username == username, User.is_active.is_(True))
            ).first()
            if user:
                return CurrentUser(id=user.id, username=user.username, role=Role(user.role))
            return CurrentUser(id=None, username=username, role=Role(payload.get("role", "viewer")))
        except Exception as exc:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token",
            ) from exc

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Authentication required",
        headers={"WWW-Authenticate": "Bearer"},
    )


def require_role(minimum: Role):
    def checker(user: CurrentUser = Depends(get_current_user)) -> CurrentUser:
        if not has_role(user.role, minimum):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Role '{minimum.value}' or higher required",
            )
        return user

    return checker
