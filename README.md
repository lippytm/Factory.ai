# Factory.ai

Connectivity workflows for GitHub, ChatGPT bots, monetary marketplaces, and
automated trading bots.

---

## Workflows

| Module | Description |
|---|---|
| `workflows/github_workflow.py` | GitHub API – repos, issues, PRs, webhooks |
| `workflows/chatgpt_workflow.py` | OpenAI ChatGPT – completions, multi-turn chat, trading signals |
| `workflows/trading_workflow.py` | Trading bots – Binance & Coinbase market data, orders, MA signals |
| `workflows/marketplace_workflow.py` | Monetary marketplaces – Stripe, PayPal, and a generic REST adapter |

---

## Quick Start

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Set environment variables

```bash
# GitHub
export GITHUB_TOKEN="ghp_..."

# ChatGPT / OpenAI
export OPENAI_API_KEY="sk-..."

# Trading (Binance – public ticker endpoint works without keys)
export BINANCE_API_KEY="..."
export BINANCE_API_SECRET="..."

# Monetary marketplace (Stripe)
export STRIPE_API_KEY="sk_live_..."
```

### 3. Run the workflow runner

```bash
python main.py
```

Override defaults with environment variables:

```bash
export GITHUB_OWNER=myorg
export GITHUB_REPO=myrepo
export TRADING_SYMBOL=ETHUSDT
export MARKETPLACE=paypal
python main.py
```

---

## Using individual workflows

```python
from workflows import GitHubWorkflow, ChatGPTWorkflow, TradingWorkflow, MarketplaceWorkflow

# GitHub
gh = GitHubWorkflow()                          # reads GITHUB_TOKEN
repos = gh.list_repos()
issues = gh.list_issues("owner", "repo")
gh.create_issue("owner", "repo", "Bug report", "Steps to reproduce …")

# ChatGPT
bot = ChatGPTWorkflow()                        # reads OPENAI_API_KEY
reply = bot.chat("What is the current trend for BTC?")
signal = bot.generate_trading_signal("RSI=72, MACD crossed up")

# Trading bot (Binance)
trader = TradingWorkflow(platform="binance")
ticker = trader.get_ticker("BTCUSDT")
signal = trader.moving_average_signal(prices=[...])   # "BUY" | "SELL" | "HOLD"

# Marketplace (Stripe)
market = MarketplaceWorkflow(marketplace="stripe")
intent = market.create_payment_intent(amount=2000, currency="usd")
balance = market.get_balance()
```

---

## Supported platforms

### Trading
- **Binance** – spot market data, market & limit orders, account balances
- **Coinbase Advanced Trade** – market data, market & limit orders, accounts

### Monetary Marketplaces
- **Stripe** – payment intents, transactions, refunds, balance
- **PayPal** – orders (Checkout), transactions, captures/refunds, balances
- **Generic REST** – configurable base URL adapter for any JSON REST marketplace

---

## Running tests

```bash
pip install pytest
pytest tests/ -v
```
