import os
from pathlib import Path

import sqlite_utils
from cryptography.hazmat.primitives.hashes import SHA256
from cryptography.hazmat.primitives.hmac import HMAC

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
DB_PATH = PROJECT_ROOT / "data" / "usage.db"

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
            "owner": str,
            "created_at": str,
            "revoked": bool,
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
    _migrate_api_keys(db)
    _migrate_usage_log(db)
    return db


def _migrate_api_keys(db):
    cols = db["api_keys"].columns_dict
    if "customer_id" not in cols:
        db["api_keys"].add_column("customer_id", str)
    if "email" not in cols:
        db["api_keys"].add_column("email", str)
    if "owner" not in cols:
        db["api_keys"].add_column("owner", str)
    if "tier" not in cols:
        db["api_keys"].add_column("tier", str)


def _migrate_usage_log(db):
    if "usage_log" not in db.tables:
        return
    cols = db["usage_log"].columns_dict
    if "latency_ms" not in cols:
        db["usage_log"].add_column("latency_ms", int)
    if "status_code" not in cols:
        db["usage_log"].add_column("status_code", int)


def hash_api_key(api_key: str) -> str:
    h = HMAC(PEPPER.encode(), SHA256())
    h.update(api_key.encode())
    return h.finalize().hex()