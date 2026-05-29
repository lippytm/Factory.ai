# Cross-Chain Agent Template

This template turns the MoonPay Trade opportunity into a Factory.ai prototype: an AI agent can describe a cross-chain intent, request a quote, wait for human approval, and then execute only when live credentials and safety controls are enabled.

## Why It Matters

MoonPay Trade packages cross-chain execution, settlement, conversion, and compliance infrastructure behind a single API. For Factory.ai, that means bots can become chain-abstracted operators instead of hardcoding separate bridge, swap, and fiat flows for every network.

## Safety Defaults

- `dry_run_default: true`
- `human_approval_required: true`
- `max_slippage_bps: 50`
- No live call is made unless `MOONPAY_TRADE_API_KEY` is set and `dry_run=False` is passed.

## Example

```python
from integrations.moonpay_trade import CrossChainExecutionRequest, MoonPayTradeClient

client = MoonPayTradeClient()
intent = CrossChainExecutionRequest(
    source_chain="solana",
    destination_chain="base",
    from_asset="USDC",
    to_asset="USDC",
    amount="25.00",
    wallet_address="demo-wallet-address",
)

quote = client.quote(intent)      # dry run by default
plan = client.execute(intent)     # dry run by default
```

## Go-Live Checklist

1. Get MoonPay Trade API access and confirm production endpoints.
2. Store `MOONPAY_TRADE_API_KEY` as an environment secret.
3. Replace demo wallet addresses with real custody/wallet infrastructure.
4. Add a human approval UI before `execute(..., dry_run=False)`.
5. Log quotes, approvals, transaction hashes, route metadata, and failures.
