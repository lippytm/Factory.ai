"""
Tests for MarketplaceWorkflow.

All HTTP calls are intercepted with unittest.mock.
"""

from unittest.mock import MagicMock, patch

import pytest

from workflows.marketplace_workflow import (
    MARKETPLACE_GENERIC,
    MARKETPLACE_PAYPAL,
    MARKETPLACE_STRIPE,
    MarketplaceWorkflow,
)


def _mock_response(data, status_code=200):
    mock = MagicMock()
    mock.status_code = status_code
    mock.raise_for_status.return_value = None
    mock.json.return_value = data
    return mock


@pytest.fixture
def stripe_wf():
    return MarketplaceWorkflow(marketplace=MARKETPLACE_STRIPE, api_key="sk_test_xxx")


@pytest.fixture
def paypal_wf():
    return MarketplaceWorkflow(
        marketplace=MARKETPLACE_PAYPAL,
        api_key="client_id",
        api_secret="client_secret",
    )


@pytest.fixture
def generic_wf():
    return MarketplaceWorkflow(
        marketplace=MARKETPLACE_GENERIC,
        api_key="api_key",
        base_url="https://api.example.com",
    )


class TestMarketplaceWorkflowInit:
    def test_invalid_marketplace_raises(self):
        with pytest.raises(ValueError, match="Unsupported marketplace"):
            MarketplaceWorkflow(marketplace="amazon")

    def test_stripe_marketplace_set(self, stripe_wf):
        assert stripe_wf.marketplace == MARKETPLACE_STRIPE

    def test_paypal_marketplace_set(self, paypal_wf):
        assert paypal_wf.marketplace == MARKETPLACE_PAYPAL

    def test_generic_marketplace_set(self, generic_wf):
        assert generic_wf.marketplace == MARKETPLACE_GENERIC


class TestCreatePaymentIntent:
    def test_stripe_create_intent(self, stripe_wf):
        intent = {"id": "pi_123", "amount": 1000, "currency": "usd"}
        with patch.object(
            stripe_wf.session, "post", return_value=_mock_response(intent)
        ):
            result = stripe_wf.create_payment_intent(1000, "usd", "Test charge")
        assert result["id"] == "pi_123"

    def test_paypal_create_order(self, paypal_wf):
        token_response = _mock_response({"access_token": "pp_token"})
        order_response = _mock_response({"id": "ORDER_456", "status": "CREATED"})
        with patch("requests.post", return_value=token_response):
            with patch.object(
                paypal_wf.session, "post", return_value=order_response
            ):
                result = paypal_wf.create_payment_intent(500, "usd")
        assert result["id"] == "ORDER_456"

    def test_generic_create_payment(self, generic_wf):
        payment = {"id": "pay_789", "amount": 200}
        with patch.object(
            generic_wf.session, "post", return_value=_mock_response(payment)
        ):
            result = generic_wf.create_payment_intent(200)
        assert result["id"] == "pay_789"


class TestListTransactions:
    def test_stripe_list_transactions(self, stripe_wf):
        transactions = [{"id": "pi_1"}, {"id": "pi_2"}]
        data = {"data": transactions}
        with patch.object(
            stripe_wf.session, "get", return_value=_mock_response(data)
        ):
            result = stripe_wf.list_transactions(limit=10)
        assert len(result) == 2

    def test_generic_list_transactions(self, generic_wf):
        transactions = [{"id": "tx_1"}]
        with patch.object(
            generic_wf.session, "get", return_value=_mock_response(transactions)
        ):
            result = generic_wf.list_transactions()
        assert len(result) == 1


class TestRefundTransaction:
    def test_stripe_refund(self, stripe_wf):
        refund = {"id": "re_123", "status": "succeeded"}
        with patch.object(
            stripe_wf.session, "post", return_value=_mock_response(refund)
        ):
            result = stripe_wf.refund_transaction("pi_123")
        assert result["id"] == "re_123"

    def test_generic_refund(self, generic_wf):
        refund = {"id": "refund_abc"}
        with patch.object(
            generic_wf.session, "post", return_value=_mock_response(refund)
        ):
            result = generic_wf.refund_transaction("tx_1", amount=100)
        assert result["id"] == "refund_abc"


class TestGetBalance:
    def test_stripe_get_balance(self, stripe_wf):
        balance = {"available": [{"amount": 10000, "currency": "usd"}]}
        with patch.object(
            stripe_wf.session, "get", return_value=_mock_response(balance)
        ):
            result = stripe_wf.get_balance()
        assert "available" in result

    def test_generic_get_balance(self, generic_wf):
        balance = {"total": 500.0, "currency": "usd"}
        with patch.object(
            generic_wf.session, "get", return_value=_mock_response(balance)
        ):
            result = generic_wf.get_balance()
        assert result["total"] == 500.0


class TestRun:
    def test_stripe_run(self, stripe_wf):
        balance = {"available": []}
        transactions = {"data": [{"id": "pi_1"}]}
        with patch.object(
            stripe_wf.session,
            "get",
            side_effect=[
                _mock_response(balance),
                _mock_response(transactions),
            ],
        ):
            result = stripe_wf.run()
        assert "balance" in result
        assert "transactions" in result
