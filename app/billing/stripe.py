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
        customer = self._client.customers.create(email=email)
        return customer.id

    def create_api_key(self, customer_id: str, email: str = "") -> str:
        api_key = "ak_" + secrets.token_hex(16)
        db = get_db()
        db["api_keys"].insert(
            {
                "api_key": api_key,
                "customer_id": customer_id,
                "email": email,
                "owner": email,
                "created_at": datetime.now(timezone.utc).isoformat(),
                "revoked": False,
            }
        )
        return api_key

    def record_usage(self, api_key: str, quantity: int):
        customer_id = self.get_customer_from_api_key(api_key)
        if customer_id is None:
            return
        subscriptions = self._client.customers.list_subscriptions(customer=customer_id)
        if not subscriptions.data:
            return
        subscription = subscriptions.data[0]
        items = self._client.subscriptions.list_items(subscription=subscription.id)
        if not items.data:
            return
        subscription_item = items.data[0]
        self._client.subscription_items.create_usage_record(subscription_item=subscription_item.id, quantity=quantity, timestamp=int(time.time()), action="increment")

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
            return {"type": event_type, "data": event["data"]["object"]}
        return None

    def process_webhook_event(self, event_type: str, event_data: dict) -> None:
        db = get_db()
        if event_type == "customer.subscription.created":
            db["subscriptions"].insert(
                {
                    "customer_id": event_data.get("customer", ""),
                    "subscription_id": event_data.get("id", ""),
                    "status": event_data.get("status", "active"),
                    "created_at": datetime.now(timezone.utc).isoformat(),
                }
            )
        elif event_type == "invoice.payment_succeeded":
            subscription_id = event_data.get("subscription", "")
            customer_id = event_data.get("customer", "")
            if subscription_id:
                rows = list(
                    db["subscriptions"].rows_where(
                        "subscription_id = ?", (subscription_id,)
                    )
                )
                if rows:
                    db["subscriptions"].update(
                        rows[0]["id"],
                        {"status": "active"},
                    )
                elif customer_id:
                    db["subscriptions"].insert(
                        {
                            "customer_id": customer_id,
                            "subscription_id": subscription_id,
                            "status": "active",
                            "created_at": datetime.now(timezone.utc).isoformat(),
                        }
                    )
        elif event_type == "invoice.payment_failed":
            subscription_id = event_data.get("subscription", "")
            if subscription_id:
                rows = list(
                    db["subscriptions"].rows_where(
                        "subscription_id = ?", (subscription_id,)
                    )
                )
                if rows:
                    db["subscriptions"].update(
                        rows[0]["id"],
                        {"status": "past_due"},
                    )