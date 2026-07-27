import os
from pathlib import Path

import sqlite_utils
from cryptography.hazmat.primitives.hashes import SHA256
from cryptography.hazmat.primitives.hmac import HMAC

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
DB_PATH = PROJECT_ROOT / "data" / "billing.db"

PEPPER = os.environ.get("API_KEY_PEPPER", "default-pepper-change-in-production")


def get_db():
    os.makedirs(DB_PATH.parent, exist_ok=True)
    db = sqlite_utils.Database(DB_PATH)
    db["api_keys"].create(
        {
            "id": int,
            "api_key": str,
            "customer_id": str,
            "email": str,
            "created_at": str,
            "is_active": bool,
            "tier": str,
        },
        pk="id",
        if_not_exists=True,
    )
    db["invoices"].create(
        {
            "id": int,
            "invoice_id": str,
            "customer_id": str,
            "api_key_hash": str,
            "amount": int,
            "status": str,
            "created_at": str,
        },
        pk="id",
        if_not_exists=True,
    )
    return db


def hash_api_key(api_key: str) -> str:
    h = HMAC(PEPPER.encode(), SHA256())
    h.update(api_key.encode())
    return h.finalize().hex()