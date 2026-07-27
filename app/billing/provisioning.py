from . import get_db, hash_api_key
from .stripe import BillingService


def provision_api_key(email: str) -> dict:
    service = BillingService()
    customer_id = service.create_customer(email)
    api_key = service.create_api_key(customer_id, email)
    return {"api_key": api_key, "customer_id": customer_id, "email": email}


def revoke_api_key(api_key: str) -> bool:
    db = get_db()
    rows = list(db["api_keys"].rows_where("api_key = ?", (api_key,)))
    if not rows:
        return False
    db["api_keys"].update(
        rows[0]["id"],
        {"revoked": True},
    )
    return True


def is_api_key_valid(api_key: str) -> dict | None:
    db = get_db()
    rows = list(db["api_keys"].rows_where("api_key = ?", (api_key,)))
    if not rows or rows[0].get("revoked"):
        return None
    return rows[0]