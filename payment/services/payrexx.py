"""
Payrexx payment service.

Handles gateway creation (hosted checkout) and webhook signature verification.

Auth: Payrexx recommends X-API-KEY header authentication (pass API secret directly).
"""

import hashlib
import hmac
import logging
from decimal import ROUND_UP, Decimal

import requests
from django.conf import settings

log = logging.getLogger(__name__)

PAYREXX_API_BASE = "https://api.payrexx.com/v1.16"


def gross_up(net: Decimal, fee_rate: Decimal, fee_flat: Decimal) -> Decimal:
    """
    Return the amount to charge the user so the school receives exactly `net`
    after Payrexx deducts its percentage fee and flat fee.

    Formula: gross = (net + flat) / (1 - rate), rounded up to the nearest centime.
    """
    return ((net + fee_flat) / (1 - fee_rate)).quantize(Decimal("0.01"), ROUND_UP)


def _fee_config(method: str) -> tuple[Decimal, Decimal]:
    cfg = settings.PAYREXX
    if method == "twint":
        return cfg["twint_fee_rate"], cfg["twint_fee_flat"]
    return cfg["card_fee_rate"], cfg["card_fee_flat"]


def _payment_methods(method: str) -> list[str]:
    if method == "twint":
        return ["twint"]
    return ["visa", "mastercard"]


def compute_gross(subscription, method: str) -> Decimal:
    """Return the gross amount (including fee) for the given payment method."""
    fee_rate, fee_flat = _fee_config(method)
    return gross_up(subscription.open_amount(), fee_rate, fee_flat)


def create_gateway(
    subscription, method: str, success_url: str, cancel_url: str
) -> tuple[str, int, Decimal]:
    """
    Create a Payrexx hosted-checkout gateway.

    Returns (payment_link_url, gateway_id, gross_amount).
    Raises requests.HTTPError on API failure.
    """
    cfg = settings.PAYREXX
    fee_rate, fee_flat = _fee_config(method)
    gross = gross_up(subscription.open_amount(), fee_rate, fee_flat)

    payload = {
        "amount": int(gross * 100),  # Payrexx expects cents
        "currency": "CHF",
        "referenceId": subscription.usi,
        "successRedirectUrl": success_url,
        "failedRedirectUrl": cancel_url,
        "cancelRedirectUrl": cancel_url,
        "fields[email][value]": subscription.user.email,
        "fields[forename][value]": subscription.user.first_name,
        "fields[surname][value]": subscription.user.last_name,
    }
    for i, pm in enumerate(_payment_methods(method)):
        payload[f"pm[{i}]"] = pm

    log.info(
        "Creating Payrexx gateway for subscription %s, method=%s, gross=CHF %s",
        subscription.usi,
        method,
        gross,
    )
    resp = requests.post(
        f"{PAYREXX_API_BASE}/Gateway/",
        params={"instance": cfg["instance"]},
        data=payload,
        headers={"X-API-KEY": cfg["api_key"]},
        timeout=15,
    )
    resp.raise_for_status()
    data = resp.json()["data"][0]
    return data["link"], data["id"], gross


def verify_webhook_signature(body: bytes, signature: str) -> bool:
    """
    Verify the X-Webhook-Signature header sent by Payrexx.
    Returns True when no signing key is configured (dev/staging without key).
    """
    key = settings.PAYREXX.get("webhook_signing_key", "")
    if not key:
        return True
    expected = hmac.new(key.encode(), body, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, signature)
