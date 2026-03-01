"""
Trading Bot Workflow
Provides connectivity to cryptocurrency and stock trading platforms
(Binance, Coinbase Advanced Trade) along with automated trading strategies.
"""

import os
import hashlib
import hmac
import logging
import time
import uuid
from urllib.parse import urlencode

import requests

logger = logging.getLogger(__name__)

# Supported platform identifiers
PLATFORM_BINANCE = "binance"
PLATFORM_COINBASE = "coinbase"

BINANCE_API_BASE = "https://api.binance.com"
COINBASE_API_BASE = "https://api.coinbase.com/api/v3"


class TradingWorkflow:
    """
    Workflow for automated trading bot connectivity.

    Supports Binance and Coinbase Advanced Trade REST APIs.
    """

    def __init__(
        self,
        platform: str = PLATFORM_BINANCE,
        api_key: str | None = None,
        api_secret: str | None = None,
    ):
        """
        Initialise the trading workflow.

        Args:
            platform: Trading platform – ``"binance"`` or ``"coinbase"``.
            api_key: API key. Falls back to ``BINANCE_API_KEY`` or
                     ``COINBASE_API_KEY`` environment variables.
            api_secret: API secret. Falls back to ``BINANCE_API_SECRET`` or
                        ``COINBASE_API_SECRET`` environment variables.
        """
        platform = platform.lower()
        if platform not in (PLATFORM_BINANCE, PLATFORM_COINBASE):
            raise ValueError(
                f"Unsupported platform '{platform}'. "
                f"Choose '{PLATFORM_BINANCE}' or '{PLATFORM_COINBASE}'."
            )
        self.platform = platform

        if platform == PLATFORM_BINANCE:
            self.api_key = api_key or os.environ.get("BINANCE_API_KEY", "")
            self.api_secret = api_secret or os.environ.get("BINANCE_API_SECRET", "")
        else:
            self.api_key = api_key or os.environ.get("COINBASE_API_KEY", "")
            self.api_secret = api_secret or os.environ.get("COINBASE_API_SECRET", "")

        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})

    # ------------------------------------------------------------------
    # Shared helpers
    # ------------------------------------------------------------------

    def _binance_sign(self, params: dict) -> dict:
        """Append a HMAC-SHA256 signature to Binance request parameters."""
        query = urlencode(params)
        signature = hmac.new(
            self.api_secret.encode(), query.encode(), hashlib.sha256
        ).hexdigest()
        params["signature"] = signature
        return params

    # ------------------------------------------------------------------
    # Market data
    # ------------------------------------------------------------------

    def get_ticker(self, symbol: str) -> dict:
        """
        Fetch the latest price ticker for a trading pair.

        Args:
            symbol: Trading pair symbol (e.g. ``"BTCUSDT"`` for Binance,
                    ``"BTC-USD"`` for Coinbase).

        Returns:
            Ticker data returned by the platform API.
        """
        if self.platform == PLATFORM_BINANCE:
            url = f"{BINANCE_API_BASE}/api/v3/ticker/price"
            params = {"symbol": symbol}
            response = self.session.get(url, params=params)
        else:
            url = f"{COINBASE_API_BASE}/brokerage/products/{symbol}"
            self.session.headers.update({"CB-ACCESS-KEY": self.api_key})
            response = self.session.get(url)
        response.raise_for_status()
        data = response.json()
        logger.info("Ticker for %s: %s", symbol, data)
        return data

    def get_order_book(self, symbol: str, limit: int = 10) -> dict:
        """
        Fetch the current order book (bids and asks) for a trading pair.

        Args:
            symbol: Trading pair symbol.
            limit: Number of price levels to return.

        Returns:
            Order book data.
        """
        if self.platform == PLATFORM_BINANCE:
            url = f"{BINANCE_API_BASE}/api/v3/depth"
            params = {"symbol": symbol, "limit": limit}
            response = self.session.get(url, params=params)
            response.raise_for_status()
            return response.json()
        else:
            url = f"{COINBASE_API_BASE}/brokerage/products/{symbol}/book"
            response = self.session.get(url, params={"limit": limit})
            response.raise_for_status()
            return response.json()

    # ------------------------------------------------------------------
    # Account / balance
    # ------------------------------------------------------------------

    def get_account_balances(self) -> list[dict]:
        """
        Retrieve non-zero asset balances for the authenticated account.

        Returns:
            List of balance objects with ``asset`` and ``free`` fields.
        """
        if self.platform == PLATFORM_BINANCE:
            params: dict = {"timestamp": int(time.time() * 1000)}
            params = self._binance_sign(params)
            url = f"{BINANCE_API_BASE}/api/v3/account"
            self.session.headers.update({"X-MBX-APIKEY": self.api_key})
            response = self.session.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            balances = [b for b in data.get("balances", []) if float(b["free"]) > 0]
            logger.info("Account has %d non-zero balances.", len(balances))
            return balances
        else:
            url = f"{COINBASE_API_BASE}/brokerage/accounts"
            self.session.headers.update({"CB-ACCESS-KEY": self.api_key})
            response = self.session.get(url)
            response.raise_for_status()
            accounts = response.json().get("accounts", [])
            logger.info("Fetched %d Coinbase accounts.", len(accounts))
            return accounts

    # ------------------------------------------------------------------
    # Order management
    # ------------------------------------------------------------------

    def place_market_order(
        self, symbol: str, side: str, quantity: float
    ) -> dict:
        """
        Place a market order.

        Args:
            symbol: Trading pair (e.g. ``"BTCUSDT"``).
            side: ``"BUY"`` or ``"SELL"``.
            quantity: Order quantity.

        Returns:
            Order confirmation returned by the platform.
        """
        side = side.upper()
        if side not in ("BUY", "SELL"):
            raise ValueError(f"Invalid order side '{side}'. Use 'BUY' or 'SELL'.")

        if self.platform == PLATFORM_BINANCE:
            params: dict = {
                "symbol": symbol,
                "side": side,
                "type": "MARKET",
                "quantity": quantity,
                "timestamp": int(time.time() * 1000),
            }
            params = self._binance_sign(params)
            url = f"{BINANCE_API_BASE}/api/v3/order"
            self.session.headers.update({"X-MBX-APIKEY": self.api_key})
            response = self.session.post(url, params=params)
        else:
            payload = {
                "client_order_id": str(uuid.uuid4()),
                "product_id": symbol,
                "side": side,
                "order_configuration": {
                    "market_market_ioc": {"base_size": str(quantity)}
                },
            }
            self.session.headers.update({"CB-ACCESS-KEY": self.api_key})
            response = self.session.post(
                f"{COINBASE_API_BASE}/brokerage/orders", json=payload
            )
        response.raise_for_status()
        order = response.json()
        logger.info("Market order placed: %s %s %s", side, quantity, symbol)
        return order

    def place_limit_order(
        self, symbol: str, side: str, quantity: float, price: float
    ) -> dict:
        """
        Place a limit order.

        Args:
            symbol: Trading pair.
            side: ``"BUY"`` or ``"SELL"``.
            quantity: Order quantity.
            price: Limit price.

        Returns:
            Order confirmation returned by the platform.
        """
        side = side.upper()
        if side not in ("BUY", "SELL"):
            raise ValueError(f"Invalid order side '{side}'. Use 'BUY' or 'SELL'.")

        if self.platform == PLATFORM_BINANCE:
            params: dict = {
                "symbol": symbol,
                "side": side,
                "type": "LIMIT",
                "timeInForce": "GTC",
                "quantity": quantity,
                "price": price,
                "timestamp": int(time.time() * 1000),
            }
            params = self._binance_sign(params)
            url = f"{BINANCE_API_BASE}/api/v3/order"
            self.session.headers.update({"X-MBX-APIKEY": self.api_key})
            response = self.session.post(url, params=params)
        else:
            payload = {
                "client_order_id": str(uuid.uuid4()),
                "product_id": symbol,
                "side": side,
                "order_configuration": {
                    "limit_limit_gtc": {
                        "base_size": str(quantity),
                        "limit_price": str(price),
                    }
                },
            }
            self.session.headers.update({"CB-ACCESS-KEY": self.api_key})
            response = self.session.post(
                f"{COINBASE_API_BASE}/brokerage/orders", json=payload
            )
        response.raise_for_status()
        order = response.json()
        logger.info(
            "Limit order placed: %s %s %s @ %s", side, quantity, symbol, price
        )
        return order

    # ------------------------------------------------------------------
    # Simple strategies
    # ------------------------------------------------------------------

    def moving_average_signal(
        self, prices: list[float], short_window: int = 5, long_window: int = 20
    ) -> str:
        """
        Compute a simple moving-average crossover trading signal.

        Args:
            prices: Ordered list of closing prices (oldest first).
            short_window: Number of periods for the short-term MA.
            long_window: Number of periods for the long-term MA.

        Returns:
            ``"BUY"``, ``"SELL"``, or ``"HOLD"``.
        """
        if len(prices) < long_window:
            logger.warning(
                "Not enough price data (%d < %d). Returning HOLD.",
                len(prices),
                long_window,
            )
            return "HOLD"

        short_ma = sum(prices[-short_window:]) / short_window
        long_ma = sum(prices[-long_window:]) / long_window

        if short_ma > long_ma:
            signal = "BUY"
        elif short_ma < long_ma:
            signal = "SELL"
        else:
            signal = "HOLD"

        logger.info(
            "MA crossover signal: %s (short_ma=%.4f, long_ma=%.4f)",
            signal,
            short_ma,
            long_ma,
        )
        return signal

    def run(self, symbol: str) -> dict:
        """
        Execute the trading workflow for a given symbol.

        Fetches the ticker and order book, then returns a summary.

        Args:
            symbol: Trading pair symbol.

        Returns:
            Dictionary with ``ticker`` and ``order_book`` keys.
        """
        logger.info(
            "Running trading workflow for %s on %s …", symbol, self.platform
        )
        ticker = self.get_ticker(symbol)
        order_book = self.get_order_book(symbol)
        result = {"ticker": ticker, "order_book": order_book}
        logger.info("Trading workflow complete for %s.", symbol)
        return result
