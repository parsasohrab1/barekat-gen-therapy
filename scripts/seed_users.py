"""Seed staging users with RBAC roles."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))

from sqlalchemy import select

from app.core.database import SessionLocal
from app.core.security import Role, generate_api_key, hash_api_key, hash_password
from app.models import User

STAGING_USERS = [
    {"username": "admin", "password": "admin123", "role": Role.ADMIN, "email": "admin@barekat.local"},
    {"username": "scientist", "password": "scientist123", "role": Role.SCIENTIST, "email": "sci@barekat.local"},
    {"username": "clinician", "password": "clinician123", "role": Role.CLINICIAN, "email": "cli@barekat.local"},
    {"username": "viewer", "password": "viewer123", "role": Role.VIEWER, "email": "view@barekat.local"},
]


def main() -> None:
    service_key = generate_api_key()
    with SessionLocal() as db:
        for entry in STAGING_USERS:
            existing = db.scalars(select(User).where(User.username == entry["username"])).first()
            if existing:
                print(f"skip: {entry['username']} already exists")
                continue
            api_hash = hash_api_key(service_key) if entry["role"] == Role.SCIENTIST else None
            user = User(
                username=entry["username"],
                email=entry["email"],
                hashed_password=hash_password(entry["password"]),
                role=entry["role"].value,
                api_key_hash=api_hash,
            )
            db.add(user)
            print(f"created: {entry['username']} ({entry['role'].value})")
        db.commit()
    print(f"\nService API key (scientist): {service_key}")


if __name__ == "__main__":
    main()
