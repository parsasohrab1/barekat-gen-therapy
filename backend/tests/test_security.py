"""Security and RBAC tests."""

from app.core.security import Role, create_access_token, has_role, hash_password, verify_password


def test_password_hash_roundtrip():
    hashed = hash_password("testpass123")
    assert verify_password("testpass123", hashed)
    assert not verify_password("wrong", hashed)


def test_jwt_create_and_role_hierarchy():
    token = create_access_token("scientist", Role.SCIENTIST.value)
    assert token
    assert has_role(Role.ADMIN, Role.VIEWER)
    assert has_role(Role.SCIENTIST, Role.VIEWER)
    assert has_role(Role.SCIENTIST, Role.CLINICIAN)  # research predict access
    assert not has_role(Role.VIEWER, Role.SCIENTIST)
    assert not has_role(Role.CLINICIAN, Role.SCIENTIST)
