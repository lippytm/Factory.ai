"""
MoonPay Trade client for Factory.ai cross-chain agent prototypes.

MoonPay Trade was announced as a single API for institutional access to 200+
chains and protocols. Public endpoint details may vary by account, so this
client keeps the base URL and path configurable while standardizing how
Factory.ai agents describe cross-chain intent.

No real transaction is sent unless ``dry_run=False`` and ``MOONPAY_TRADE_API_KEY``
is configured.
"""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from dataclasses import asdict, dataclass
from typing import Any


@dataclass(frozen=True)
class CrossChainExecutionRequest:
    """A chain-abstracted transaction intent for an AI agent."""

    source_chain: str
    destination_chain: str
    from_asset: str
    to_asset: str
    amount: str
    wallet_address: str
    destination_address: str | None = None
    slippage_bps: int = 50
    memo: str = "Factory.ai cross-chain agent execution"

    def payload(self) -> dict[str, Any]:
        data = asdict(self)
        if not data["destination_address"]:
            data["destination_address"] = self.wallet_address
        return data


class MoonPayTradeClient:
    """Thin configurable client for MoonPay Trade-style cross-chain execution."""

    DEFAULT_BASE_URL = "https://api.moonpay.com"
    DEFAULT_EXECUTION_PATH = "/trade/v1/execute"
    DEFAULT_QUOTE_PATH = "/trade/v1/quote"

    def __init__(
        self,
        api_key: str | None = None,
        base_url: str | None = None,
        execution_path: str | None = None,
        quote_path: str | None = None,
    ) -> None:
        self.api_key = api_key or os.getenv("MOONPAY_TRADE_API_KEY", "")
        self.base_url = (base_url or os.getenv("MOONPAY_TRADE_BASE_URL", self.DEFAULT_BASE_URL)).rstrip("/")
        self.execution_path = execution_path or os.getenv("MOONPAY_TRADE_EXECUTION_PATH", self.DEFAULT_EXECUTION_PATH)
        self.quote_path = quote_path or os.getenv("MOONPAY_TRADE_QUOTE_PATH", self.DEFAULT_QUOTE_PATH)

    def build_execution_payload(self, request: CrossChainExecutionRequest) -> dict[str, Any]:
        """Build the payload an agent would submit for cross-chain execution."""
        return {
            "type": "cross_chain_execution",
            "intent": request.payload(),
            "controls": {
                "human_approval_required": True,
                "dry_run_default": True,
                "max_slippage_bps": request.slippage_bps,
            },
            "metadata": {
                "source": "Factory.ai",
                "memo": request.memo,
            },
        }

    def quote(self, request: CrossChainExecutionRequest, *, dry_run: bool = True) -> dict[str, Any]:
        """Request a quote or return a local dry-run quote payload."""
        payload = self.build_execution_payload(request)
        if dry_run:
            return {
                "dry_run": True,
                "endpoint": f"{self.base_url}{self.quote_path}",
                "payload": payload,
                "next_step": "Set MOONPAY_TRADE_API_KEY and dry_run=False after MoonPay approves API access.",
            }
        return self._post(self.quote_path, payload)

    def execute(self, request: CrossChainExecutionRequest, *, dry_run: bool = True) -> dict[str, Any]:
        """Execute a cross-chain intent or return the dry-run execution plan."""
        payload = self.build_execution_payload(request)
        if dry_run:
            return {
                "dry_run": True,
                "endpoint": f"{self.base_url}{self.execution_path}",
                "payload": payload,
                "approval_gate": "Human must review quote, route, fees, and wallet before live execution.",
            }
        return self._post(self.execution_path, payload)

    def _post(self, path: str, body: dict[str, Any]) -> dict[str, Any]:
        if not self.api_key:
            raise RuntimeError("MOONPAY_TRADE_API_KEY is required for live MoonPay Trade calls")
        request = urllib.request.Request(
            f"{self.base_url}{path}",
            data=json.dumps(body).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "User-Agent": "Factory.ai MoonPay Trade Agent Prototype",
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=60) as response:
                return json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")
            raise RuntimeError(f"MoonPay Trade API error {exc.code}: {detail}") from exc
        except urllib.error.URLError as exc:
            raise RuntimeError(f"MoonPay Trade request failed: {exc}") from exc
