"""
Factory.ai – Main entry point

Demonstrates running connectivity workflows for GitHub, ChatGPT,
trading bots, and monetary marketplaces.

Set the required environment variables before running:
  GITHUB_TOKEN       – GitHub personal access token
  OPENAI_API_KEY     – OpenAI API key
  BINANCE_API_KEY    – Binance API key   (optional)
  BINANCE_API_SECRET – Binance API secret (optional)
  STRIPE_API_KEY     – Stripe secret key  (optional)

Usage:
    python main.py
"""

import logging
import os
import sys

from workflows import (
    ChatGPTWorkflow,
    GitHubWorkflow,
    MarketplaceWorkflow,
    TradingWorkflow,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(name)s – %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


def run_github(owner: str, repo: str) -> None:
    """Run the GitHub connectivity workflow."""
    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        logger.warning("GITHUB_TOKEN not set – skipping GitHub workflow.")
        return
    wf = GitHubWorkflow(token=token)
    result = wf.run(owner, repo)
    logger.info(
        "GitHub: %d open issues, %d open PRs in %s/%s.",
        len(result["issues"]),
        len(result["pull_requests"]),
        owner,
        repo,
    )


def run_chatgpt(prompt: str) -> None:
    """Run the ChatGPT connectivity workflow."""
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        logger.warning("OPENAI_API_KEY not set – skipping ChatGPT workflow.")
        return
    wf = ChatGPTWorkflow(api_key=api_key)
    reply = wf.run(prompt)
    logger.info("ChatGPT reply: %s", reply[:200])


def run_trading(symbol: str, platform: str = "binance") -> None:
    """Run the trading bot workflow."""
    wf = TradingWorkflow(platform=platform)
    result = wf.run(symbol)
    logger.info("Trading ticker: %s", result["ticker"])


def run_marketplace(marketplace: str = "stripe") -> None:
    """Run the marketplace workflow."""
    wf = MarketplaceWorkflow(marketplace=marketplace)
    result = wf.run()
    logger.info(
        "Marketplace balance: %s  |  Transactions: %d",
        result["balance"],
        len(result["transactions"]),
    )


def main() -> None:
    logger.info("=== Factory.ai Workflow Runner ===")

    # GitHub workflow
    github_owner = os.environ.get("GITHUB_OWNER", "lippytm")
    github_repo = os.environ.get("GITHUB_REPO", "Factory.ai")
    run_github(github_owner, github_repo)

    # ChatGPT workflow
    chatgpt_prompt = os.environ.get(
        "CHATGPT_PROMPT",
        "Summarise the current state of AI-powered trading bots in two sentences.",
    )
    run_chatgpt(chatgpt_prompt)

    # Trading workflow (public ticker endpoint – no auth required)
    trading_symbol = os.environ.get("TRADING_SYMBOL", "BTCUSDT")
    trading_platform = os.environ.get("TRADING_PLATFORM", "binance")
    run_trading(trading_symbol, trading_platform)

    # Marketplace workflow
    marketplace = os.environ.get("MARKETPLACE", "stripe")
    run_marketplace(marketplace)

    logger.info("=== All workflows complete ===")


if __name__ == "__main__":
    main()
