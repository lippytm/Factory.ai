from integrations.moonpay_trade import CrossChainExecutionRequest, MoonPayTradeClient


def sample_request() -> CrossChainExecutionRequest:
    return CrossChainExecutionRequest(
        source_chain="solana",
        destination_chain="base",
        from_asset="USDC",
        to_asset="USDC",
        amount="25.00",
        wallet_address="demo-wallet",
    )


def test_payload_defaults_destination_address_to_wallet():
    client = MoonPayTradeClient(api_key="test")
    payload = client.build_execution_payload(sample_request())

    assert payload["type"] == "cross_chain_execution"
    assert payload["intent"]["destination_address"] == "demo-wallet"
    assert payload["controls"]["human_approval_required"] is True
    assert payload["controls"]["dry_run_default"] is True


def test_quote_dry_run_does_not_require_live_api_call():
    client = MoonPayTradeClient(api_key="")
    quote = client.quote(sample_request())

    assert quote["dry_run"] is True
    assert quote["endpoint"].endswith("/trade/v1/quote")
    assert quote["payload"]["intent"]["amount"] == "25.00"


def test_execute_dry_run_returns_approval_gate():
    client = MoonPayTradeClient(api_key="")
    plan = client.execute(sample_request())

    assert plan["dry_run"] is True
    assert "Human" in plan["approval_gate"]
    assert plan["endpoint"].endswith("/trade/v1/execute")
