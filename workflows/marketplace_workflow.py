"""
Monetary Marketplace Workflow
Provides connectivity to popular monetary marketplaces: Stripe, PayPal,
and a generic REST marketplace adapter.
"""

import os
import logging
import requests

logger = logging.getLogger(__name__)

MARKETPLACE_STRIPE = "stripe"
MARKETPLACE_PAYPAL = "paypal"
MARKETPLACE_GENERIC = "generic"

STRIPE_API_BASE = "https://api.stripe.com/v1"
PAYPAL_API_BASE = "https://api-m.paypal.com"


class MarketplaceWorkflow:
    """
    Workflow for monetary marketplace connectivity and payment automation.

    Supports Stripe, PayPal, and a generic REST marketplace adapter.
    """

    def __init__(
        self,
        marketplace: str = MARKETPLACE_STRIPE,
        api_key: str | None = None,
        api_secret: str | None = None,
        base_url: str | None = None,
    ):
        """
        Initialise the marketplace workflow.

        Args:
            marketplace: Target marketplace – ``"stripe"``, ``"paypal"``,
                         or ``"generic"``.
            api_key: API key / client ID. Falls back to ``STRIPE_API_KEY``,
                     ``PAYPAL_CLIENT_ID``, or ``MARKETPLACE_API_KEY``
                     environment variables.
            api_secret: API secret / client secret. Falls back to
                        ``PAYPAL_CLIENT_SECRET`` or ``MARKETPLACE_API_SECRET``
                        environment variables.
            base_url: Base URL for the ``"generic"`` marketplace adapter.
        """
        marketplace = marketplace.lower()
        if marketplace not in (
            MARKETPLACE_STRIPE,
            MARKETPLACE_PAYPAL,
            MARKETPLACE_GENERIC,
        ):
            raise ValueError(
                f"Unsupported marketplace '{marketplace}'. "
                "Choose 'stripe', 'paypal', or 'generic'."
            )
        self.marketplace = marketplace
        self.session = requests.Session()

        if marketplace == MARKETPLACE_STRIPE:
            self.api_key = api_key or os.environ.get("STRIPE_API_KEY", "")
            self.session.auth = (self.api_key, "")

        elif marketplace == MARKETPLACE_PAYPAL:
            self.client_id = api_key or os.environ.get("PAYPAL_CLIENT_ID", "")
            self.client_secret = api_secret or os.environ.get(
                "PAYPAL_CLIENT_SECRET", ""
            )
            self._paypal_token: str | None = None

        else:  # generic
            self.api_key = api_key or os.environ.get("MARKETPLACE_API_KEY", "")
            self.api_secret = api_secret or os.environ.get(
                "MARKETPLACE_API_SECRET", ""
            )
            self.base_url = base_url or os.environ.get(
                "MARKETPLACE_BASE_URL", "https://api.example-marketplace.com"
            )
            self.session.headers.update({"Authorization": f"Bearer {self.api_key}"})

    # ------------------------------------------------------------------
    # PayPal OAuth
    # ------------------------------------------------------------------

    def _paypal_authenticate(self) -> str:
        """
        Obtain a PayPal OAuth 2.0 access token.

        Returns:
            Access token string.
        """
        url = f"{PAYPAL_API_BASE}/v1/oauth2/token"
        response = requests.post(
            url,
            auth=(self.client_id, self.client_secret),
            data={"grant_type": "client_credentials"},
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        response.raise_for_status()
        token = response.json()["access_token"]
        self._paypal_token = token
        self.session.headers.update({"Authorization": f"Bearer {token}"})
        logger.info("PayPal authentication successful.")
        return token

    # ------------------------------------------------------------------
    # Payment / charge helpers
    # ------------------------------------------------------------------

    def create_payment_intent(
        self, amount: int, currency: str = "usd", description: str = ""
    ) -> dict:
        """
        Create a payment intent / charge on the configured marketplace.

        Args:
            amount: Amount in the smallest currency unit (e.g. cents for USD).
            currency: ISO 4217 currency code (default ``"usd"``).
            description: Optional description for the transaction.

        Returns:
            Payment intent / order object returned by the platform.
        """
        if self.marketplace == MARKETPLACE_STRIPE:
            payload = {
                "amount": amount,
                "currency": currency,
                "description": description,
            }
            response = self.session.post(
                f"{STRIPE_API_BASE}/payment_intents", data=payload
            )
            response.raise_for_status()
            intent = response.json()
            logger.info(
                "Stripe PaymentIntent created: %s (%d %s)",
                intent["id"],
                amount,
                currency,
            )
            return intent

        elif self.marketplace == MARKETPLACE_PAYPAL:
            if not self._paypal_token:
                self._paypal_authenticate()
            amount_value = f"{amount / 100:.2f}"
            payload = {
                "intent": "CAPTURE",
                "purchase_units": [
                    {
                        "amount": {"currency_code": currency.upper(), "value": amount_value},
                        "description": description,
                    }
                ],
            }
            response = self.session.post(
                f"{PAYPAL_API_BASE}/v2/checkout/orders", json=payload
            )
            response.raise_for_status()
            order = response.json()
            logger.info("PayPal order created: %s", order["id"])
            return order

        else:  # generic
            payload = {
                "amount": amount,
                "currency": currency,
                "description": description,
            }
            response = self.session.post(
                f"{self.base_url}/payments", json=payload
            )
            response.raise_for_status()
            return response.json()

    def list_transactions(self, limit: int = 20) -> list[dict]:
        """
        Retrieve recent transactions / payment intents.

        Args:
            limit: Maximum number of records to return.

        Returns:
            List of transaction objects.
        """
        if self.marketplace == MARKETPLACE_STRIPE:
            response = self.session.get(
                f"{STRIPE_API_BASE}/payment_intents",
                params={"limit": limit},
            )
            response.raise_for_status()
            data = response.json()
            transactions = data.get("data", [])
            logger.info("Retrieved %d Stripe transactions.", len(transactions))
            return transactions

        elif self.marketplace == MARKETPLACE_PAYPAL:
            if not self._paypal_token:
                self._paypal_authenticate()
            response = self.session.get(
                f"{PAYPAL_API_BASE}/v1/reporting/transactions",
                params={"page_size": limit},
            )
            response.raise_for_status()
            items = response.json().get("transaction_details", [])
            logger.info("Retrieved %d PayPal transactions.", len(items))
            return items

        else:  # generic
            response = self.session.get(
                f"{self.base_url}/transactions", params={"limit": limit}
            )
            response.raise_for_status()
            return response.json()

    def refund_transaction(self, transaction_id: str, amount: int | None = None) -> dict:
        """
        Issue a full or partial refund for a transaction.

        Args:
            transaction_id: The ID of the payment / charge to refund.
            amount: Amount to refund in smallest currency units. When
                    omitted, the full transaction amount is refunded.

        Returns:
            Refund object returned by the platform.
        """
        if self.marketplace == MARKETPLACE_STRIPE:
            payload: dict = {"payment_intent": transaction_id}
            if amount is not None:
                payload["amount"] = amount
            response = self.session.post(
                f"{STRIPE_API_BASE}/refunds", data=payload
            )
            response.raise_for_status()
            refund = response.json()
            logger.info("Stripe refund created: %s", refund["id"])
            return refund

        elif self.marketplace == MARKETPLACE_PAYPAL:
            if not self._paypal_token:
                self._paypal_authenticate()
            payload = {}
            if amount is not None:
                payload["amount"] = {"value": f"{amount / 100:.2f}"}
            response = self.session.post(
                f"{PAYPAL_API_BASE}/v2/payments/captures/{transaction_id}/refund",
                json=payload,
            )
            response.raise_for_status()
            refund = response.json()
            logger.info("PayPal refund created: %s", refund["id"])
            return refund

        else:  # generic
            payload = {"transaction_id": transaction_id}
            if amount is not None:
                payload["amount"] = amount
            response = self.session.post(
                f"{self.base_url}/refunds", json=payload
            )
            response.raise_for_status()
            return response.json()

    def get_balance(self) -> dict:
        """
        Retrieve the current account balance.

        Returns:
            Balance object returned by the platform.
        """
        if self.marketplace == MARKETPLACE_STRIPE:
            response = self.session.get(f"{STRIPE_API_BASE}/balance")
            response.raise_for_status()
            balance = response.json()
            logger.info("Stripe balance fetched.")
            return balance

        elif self.marketplace == MARKETPLACE_PAYPAL:
            if not self._paypal_token:
                self._paypal_authenticate()
            response = self.session.get(
                f"{PAYPAL_API_BASE}/v1/reporting/balances"
            )
            response.raise_for_status()
            balance = response.json()
            logger.info("PayPal balance fetched.")
            return balance

        else:  # generic
            response = self.session.get(f"{self.base_url}/balance")
            response.raise_for_status()
            return response.json()

    def run(self) -> dict:
        """
        Execute the marketplace workflow.

        Fetches the current balance and lists recent transactions.

        Returns:
            Dictionary with ``balance`` and ``transactions`` keys.
        """
        logger.info("Running marketplace workflow for %s …", self.marketplace)
        balance = self.get_balance()
        transactions = self.list_transactions()
        result = {"balance": balance, "transactions": transactions}
        logger.info(
            "Marketplace workflow complete: %d transactions.", len(transactions)
        )
        return result
