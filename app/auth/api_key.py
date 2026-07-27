import os
import secrets
import sqlite_utils
from datetime import datetime, timezone
from fastapi import Depends, HTTPException, Request

DB_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "data",
    "usage.db",
)


def _get_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    db = sqlite_utils.Database(DB_PATH)
    db["api_keys"].create(
        {
            "id": int,
            "api_key": str,
            "owner": str,
            "created_at": str,
            "revoked": bool,
            "tier": str,
        },
        pk="id",
        if_not_exists=True,
    )
    db["usage_log"].create(
        {
            "id": int,
            "api_key": str,
            "model": str,
            "duration_ms": int,
            "input_size_bytes": int,
            "timestamp": str,
        },
        pk="id",
        if_not_exists=True,
    )
    return db


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def generate_api_key(owner: str, tier: str = "free") -> str:
    prefix = os.getenv("API_KEY_PREFIX", "ak_")
    key = prefix + secrets.token_hex(16)
    db = _get_db()
    db["api_keys"].insert(
        {
            "api_key": key,
            "owner": owner,
            "created_at": _now(),
            "revoked": False,
            "tier": tier,
        }
    )
    return key


def validate_api_key(key: str) -> bool:
    db = _get_db()
    rows = list(db["api_keys"].rows_where("api_key = ?", (key,)))
    if not rows:
        return False
    return not rows[0].get("revoked", False)


def get_api_key_owner(key: str) -> str | None:
    db = _get_db()
    rows = list(db["api_keys"].rows_where("api_key = ?", (key,)))
    if not rows or rows[0].get("revoked", False):
        return None
    return rows[0].get("owner")


def get_api_key_tier(key: str) -> str:
    db = _get_db()
    rows = list(db["api_keys"].rows_where("api_key = ?", (key,)))
    if not rows or rows[0].get("revoked", False):
        return "free"
    return rows[0].get("tier", "free")


def get_daily_usage_count(api_key: str) -> int:
    db = _get_db()
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