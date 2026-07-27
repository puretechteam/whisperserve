import os
import secrets
import time
from datetime import datetime, timezone

import stripe

from . import get_db, hash_api_key

WEBHOOK_SECRET = os.environ.get("STRIPE_WEBHOOK_SECRET", "")


class BillingService:
    def __init__(self):
        self._client = stripe.StripeClient(
            os.environ.get("STRIPE_SECRET_KEY", "")
        )

    def create_customer(self, email: str) -> str:
        customer = self._client.v1.customers.create(params={"email": email})
        return customer.id

    def create_api_key(self, customer_id: str, email: str = "") -> str:
        api_key = "ak_" + secrets.token_hex(16)
        db = get_db()
        db["api_keys"].insert(
            {
                "api_key": api_key,
                "customer_id": customer_id,
                "email": email,
                "created_at": datetime.now(timezone.utc).isoformat(),
                "revoked": False,
            }
        )
        return api_key

    def record_usage(self, api_key: str, quantity: int):
        customer_id = self.get_customer_from_api_key(api_key)
        if customer_id is None:
            return
        subscriptions = self._client.v1.customers.list_subscriptions(
            params={"customer": customer_id},
        )
        if not subscriptions.data:
            return
        subscription = subscriptions.data[0]
        items = self._client.v1.subscriptions.list_items(
            params={"subscription": subscription.id},
        )
        if not items.data:
            return
        subscription_item = items.data[0]
        self._client.v1.subscription_items.create_usage_record(
            params={
                "subscription_item": subscription_item.id,
                "quantity": quantity,
                "timestamp": int(time.time()),
                "action": "increment",
            },
        )

    def get_customer_from_api_key(self, api_key: str) -> str | None:
        db = get_db()
        rows = list(db["api_keys"].rows_where("api_key = ?", (api_key,)))
        if not rows or rows[0].get("revoked"):
            return None
        return rows[0].get("customer_id")

    def handle_webhook(self, payload: bytes, sig_header: str) -> dict | None:
        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, WEBHOOK_SECRET,
            )
        except (stripe.error.SignatureVerificationError, ValueError):
            return None
        event_type = event["type"]
        if event_type in (
            "customer.subscription.created",
            "invoice.payment_succeeded",
            "invoice.payment_failed",
        ):
            return event["data"]["object"]
        return None