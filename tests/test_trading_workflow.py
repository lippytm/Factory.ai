"""
Tests for TradingWorkflow.

All HTTP calls are intercepted with unittest.mock.
"""

from unittest.mock import MagicMock, patch

import pytest

from workflows.trading_workflow import (
    PLATFORM_BINANCE,
    PLATFORM_COINBASE,
    TradingWorkflow,
)


def _mock_response(data, status_code=200):
    mock = MagicMock()
    mock.status_code = status_code
    mock.raise_for_status.return_value = None
    mock.json.return_value = data
    return mock


@pytest.fixture
def binance_wf():
    return TradingWorkflow(
        platform=PLATFORM_BINANCE,
        api_key="test-key",
        api_secret="test-secret",
    )


@pytest.fixture
def coinbase_wf():
    return TradingWorkflow(
        platform=PLATFORM_COINBASE,
        api_key="test-key",
        api_secret="test-secret",
    )


class TestTradingWorkflowInit:
    def test_invalid_platform_raises(self):
        with pytest.raises(ValueError, match="Unsupported platform"):
            TradingWorkflow(platform="unknown")

    def test_binance_platform_set(self, binance_wf):
        assert binance_wf.platform == PLATFORM_BINANCE

    def test_coinbase_platform_set(self, coinbase_wf):
        assert coinbase_wf.platform == PLATFORM_COINBASE


class TestGetTicker:
    def test_binance_get_ticker(self, binance_wf):
        ticker = {"symbol": "BTCUSDT", "price": "45000.00"}
        with patch.object(
            binance_wf.session, "get", return_value=_mock_response(ticker)
        ):
            result = binance_wf.get_ticker("BTCUSDT")
        assert result["symbol"] == "BTCUSDT"

    def test_coinbase_get_ticker(self, coinbase_wf):
        ticker = {"product_id": "BTC-USD", "price": "45000"}
        with patch.object(
            coinbase_wf.session, "get", return_value=_mock_response(ticker)
        ):
            result = coinbase_wf.get_ticker("BTC-USD")
        assert result["product_id"] == "BTC-USD"


class TestGetOrderBook:
    def test_binance_order_book(self, binance_wf):
        book = {"bids": [["45000", "0.5"]], "asks": [["45001", "0.3"]]}
        with patch.object(
            binance_wf.session, "get", return_value=_mock_response(book)
        ):
            result = binance_wf.get_order_book("BTCUSDT")
        assert "bids" in result


class TestPlaceOrder:
    def test_market_order_buy(self, binance_wf):
        order = {"orderId": 1, "status": "FILLED"}
        with patch.object(
            binance_wf.session, "post", return_value=_mock_response(order)
        ):
            result = binance_wf.place_market_order("BTCUSDT", "BUY", 0.001)
        assert result["orderId"] == 1

    def test_market_order_invalid_side(self, binance_wf):
        with pytest.raises(ValueError, match="Invalid order side"):
            binance_wf.place_market_order("BTCUSDT", "HOLD", 0.001)

    def test_limit_order(self, binance_wf):
        order = {"orderId": 2, "status": "NEW"}
        with patch.object(
            binance_wf.session, "post", return_value=_mock_response(order)
        ):
            result = binance_wf.place_limit_order("BTCUSDT", "SELL", 0.001, 50000)
        assert result["orderId"] == 2

    def test_limit_order_invalid_side(self, binance_wf):
        with pytest.raises(ValueError, match="Invalid order side"):
            binance_wf.place_limit_order("BTCUSDT", "MAYBE", 0.001, 50000)


class TestMovingAverageSignal:
    def test_buy_signal(self, binance_wf):
        # Short MA > Long MA → BUY
        prices = [100] * 15 + [110] * 5  # last 5 prices higher
        signal = binance_wf.moving_average_signal(prices, short_window=5, long_window=20)
        assert signal == "BUY"

    def test_sell_signal(self, binance_wf):
        # Short MA < Long MA → SELL
        prices = [110] * 15 + [100] * 5
        signal = binance_wf.moving_average_signal(prices, short_window=5, long_window=20)
        assert signal == "SELL"

    def test_hold_signal_equal_ma(self, binance_wf):
        prices = [100] * 20
        signal = binance_wf.moving_average_signal(prices, short_window=5, long_window=20)
        assert signal == "HOLD"

    def test_not_enough_data_returns_hold(self, binance_wf):
        signal = binance_wf.moving_average_signal([100, 110], short_window=5, long_window=20)
        assert signal == "HOLD"


class TestRun:
    def test_run_returns_ticker_and_book(self, binance_wf):
        ticker = {"symbol": "BTCUSDT", "price": "45000"}
        book = {"bids": [], "asks": []}
        with patch.object(
            binance_wf.session,
            "get",
            side_effect=[_mock_response(ticker), _mock_response(book)],
        ):
            result = binance_wf.run("BTCUSDT")
        assert result["ticker"] == ticker
        assert result["order_book"] == book
