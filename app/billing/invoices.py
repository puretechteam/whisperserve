import os
from datetime import datetime, timezone

import stripe

from . import get_db, hash_api_key
from .stripe import BillingService
from app.logging.usage import get_usage


def generate_invoice(customer_id: str) -> dict:
    service = BillingService()
    invoice = service._client.v1.invoices.create(
        params={"customer": customer_id, "auto_advance": True},
    )
    finalized = service._client.v1.invoices.finalize_invoice(
        params={"invoice": invoice.id},
    )
    return {
        "invoice_id": finalized.id,
        "customer_id": customer_id,
        "amount": finalized.amount_total,
        "status": finalized.status,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }


def generate_invoice_for_usage(api_key: str) -> dict | None:
    service = BillingService()
    customer_id = service.get_customer_from_api_key(api_key)
    if customer_id is None:
        return None

    usage = get_usage(api_key, days=30)
    if usage["total_requests"] == 0:
        return None

    amount_cents = _calculate_amount(usage)

    invoice = service._client.v1.invoices.create(
        params={"customer": customer_id, "auto_advance": True},
    )

    service._client.v1.invoices.create_line_item(
        params={
            "invoice": invoice.id,
            "price_data": {
                "currency": "usd",
                "product_data": {"name": "API Usage"},
                "unit_amount": amount_cents,
            },
            "quantity": 1,
        },
    )

    finalized = service._client.v1.invoices.finalize_invoice(
        params={"invoice": invoice.id},
    )

    db = get_db()
    db["invoices"].insert(
        {
            "invoice_id": finalized.id,
            "customer_id": customer_id,
            "api_key_hash": hash_api_key(api_key),
            "amount": finalized.amount_total,
            "status": finalized.status,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
    )

    return {
        "invoice_id": finalized.id,
        "customer_id": customer_id,
        "amount": finalized.amount_total,
        "status": finalized.status,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }


def _calculate_amount(usage: dict) -> int:
    input_bytes = usage["total_input_bytes"]
    duration_ms = usage["total_duration_ms"]
    input_cost = input_bytes / (1024 * 1024) * 0.50
    duration_cost = duration_ms / 1000 * 0.02
    total = input_cost + duration_cost
    return max(int(total * 100), 1)


def get_all_active_customers() -> list[str]:
    db = get_db()
    rows = list(db["api_keys"].rows_where("revoked = ?", (False,)))
    return list(set(r["customer_id"] for r in rows if r.get("customer_id")))


def generate_invoices_for_all_active() -> list[dict]:
    customer_ids = get_all_active_customers()
    results = []
    for customer_id in customer_ids:
        try:
            result = generate_invoice(customer_id)
            results.append(result)
        except Exception:
            continue
    return results