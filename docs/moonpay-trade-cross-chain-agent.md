# MoonPay Trade Cross-Chain Agent Prototype

## Opportunity

MoonPay launched MoonPay Trade after acquiring Decent.xyz, positioning it as a single API for institutions and enterprises to access 200+ blockchains and protocols. This is a strong fit for Factory.ai because agents need chain-abstracted execution instead of bespoke bridge code.

## Agent Flow

```text
User/strategy prompt
  ↓
Factory.ai agent extracts transaction intent
  ↓
MoonPayTradeClient.quote(intent, dry_run=True)
  ↓
Human reviews route, amount, fees, destination, compliance flags
  ↓
MoonPayTradeClient.execute(intent, dry_run=False)
  ↓
AllBots/Factory logs transaction hash, route, approval receipt, outcome
```

## Implementation Added

- `integrations/moonpay_trade/client.py` — configurable API client and payload builder.
- `templates/cross_chain_agent/bot.yaml` — Factory template manifest.
- `templates/cross_chain_agent/README.md` — setup and safety guide.
- `tests/test_moonpay_trade_client.py` — dry-run behavior and payload tests.

## Environment

```bash
export MOONPAY_TRADE_API_KEY="..."
export MOONPAY_TRADE_BASE_URL="https://api.moonpay.com"
export MOONPAY_TRADE_QUOTE_PATH="/trade/v1/quote"
export MOONPAY_TRADE_EXECUTION_PATH="/trade/v1/execute"
```

The paths are configurable because MoonPay may issue account-specific or versioned API endpoints.

## Human Approval Requirements

Before any live execution, show the operator:

- Source chain and asset
- Destination chain and asset
- Amount
- Destination address
- Route/bridge/liquidity source
- Estimated fees
- Slippage limit
- Compliance/KYC status
- Quote expiry

## Next Build Step

Connect this template to an AllBots approval workflow so the bot can produce a quote card with **Approve / Reject** buttons before calling `execute(..., dry_run=False)`.
