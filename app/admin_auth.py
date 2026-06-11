import hashlib
import hmac

from fastapi import Header, HTTPException

from app.config import config


def create_admin_token() -> str:
    return hmac.new(
        config.secret_key.encode(),
        b"admin-session",
        hashlib.sha256,
    ).hexdigest()


def verify_admin_password(password: str) -> bool:
    return hmac.compare_digest(password, config.admin_password)


def verify_admin_token(token: str) -> bool:
    expected = create_admin_token()
    return hmac.compare_digest(token, expected)


def require_admin(x_admin_token: str = Header(..., alias="X-Admin-Token")) -> None:
    if not verify_admin_token(x_admin_token):
        raise HTTPException(status_code=401, detail="Unauthorized")
