import os
import secrets
from datetime import datetime, timezone
from fastapi import Depends, HTTPException, Request

from app.billing import get_db


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def generate_api_key(owner: str, tier: str = "free", customer_id: str = "", email: str = "") -> str:
    prefix = os.getenv("API_KEY_PREFIX", "ak_")
    key = prefix + secrets.token_hex(16)
    db = get_db()
    db["api_keys"].insert(
        {
            "api_key": key,
            "owner": owner,
            "customer_id": customer_id,
            "email": email,
            "created_at": _now(),
            "revoked": False,
            "tier": tier,
        }
    )
    return key


def validate_api_key(key: str) -> bool:
    db = get_db()
    rows = list(db["api_keys"].rows_where("api_key = ?", (key,)))
    if not rows:
        return False
    return not rows[0].get("revoked", False)


def get_api_key_owner(key: str) -> str | None:
    db = get_db()
    rows = list(db["api_keys"].rows_where("api_key = ?", (key,)))
    if not rows or rows[0].get("revoked", False):
        return None
    return rows[0].get("owner")


def get_api_key_tier(key: str) -> str:
    db = get_db()
    rows = list(db["api_keys"].rows_where("api_key = ?", (key,)))
    if not rows or rows[0].get("revoked", False):
        return "free"
    return rows[0].get("tier", "free")


def get_daily_usage_count(api_key: str) -> int:
    db = get_db()
    today = datetime.now(timezone.utc).date().isoformat()
    rows = list(
        db["usage_log"].rows_where(
            "api_key = ? AND timestamp >= ?",
            (api_key, today),
        )
    )
    return len(rows)


async def get_api_key(request: Request) -> str:
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid Authorization header")
    key = auth_header[7:]
    if not validate_api_key(key):
        raise HTTPException(status_code=401, detail="Invalid API key")
    return key