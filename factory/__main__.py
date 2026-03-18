#!/usr/bin/env python3
"""
factory.__main__ – Factory.ai command-line interface.

Entry point for the ``python -m factory`` command.  Provides three
sub-commands:

``generate``
    Load a bot template, merge in a custom name, and print the resulting
    manifest as JSON.  Useful for previewing or scaffolding a new bot.

``deploy``
    Validate a template manifest and deploy a single bot to the AllBots
    platform (requires ``ALLBOTS_API_KEY`` to be set in the environment).

``swarm``
    Coordinate multiple already-deployed bots into a swarm via the
    AllBots API (requires ``ALLBOTS_API_KEY``).

Usage examples::

    python -m factory generate --template templates/customer_support --name MyBot
    python -m factory deploy   --template templates/customer_support --name MyBot --env production
    python -m factory swarm    --bots "BotA,BotB" --coordinator round-robin --env production
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

import yaml

from integrations.allbots.client import AllBotsClient


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _load_manifest(template: str) -> dict[str, Any]:
    """Load and parse *template*/bot.yaml, raising SystemExit on failure."""
    template_path = Path(template)
    manifest_path = template_path / "bot.yaml"
    if not manifest_path.exists():
        print(
            f"Error: No bot.yaml found at '{manifest_path}'.",
            file=sys.stderr,
        )
        sys.exit(1)
    with manifest_path.open() as fh:
        data: dict[str, Any] = yaml.safe_load(fh) or {}
    return data


# ---------------------------------------------------------------------------
# Sub-command handlers
# ---------------------------------------------------------------------------

def cmd_generate(args: argparse.Namespace) -> int:
    """Print a merged bot manifest to stdout without deploying anything."""
    manifest = _load_manifest(args.template)
    manifest["name"] = args.name
    print(json.dumps(manifest, indent=2))
    return 0


def cmd_deploy(args: argparse.Namespace) -> int:
    """Deploy a single bot to the AllBots platform."""
    manifest = _load_manifest(args.template)
    if args.name:
        manifest["name"] = args.name
    if args.env:
        manifest.setdefault("deployment", {})["environment_target"] = args.env

    client = AllBotsClient()
    try:
        result = client.deploy_bot(manifest)
    except RuntimeError as exc:
        print(f"Deployment failed: {exc}", file=sys.stderr)
        return 1

    print(json.dumps(result, indent=2))
    return 0


def cmd_swarm(args: argparse.Namespace) -> int:
    """Deploy a swarm of bots to the AllBots platform."""
    bots = [b.strip() for b in args.bots.split(",") if b.strip()]
    if not bots:
        print("Error: --bots must be a non-empty comma-separated list.", file=sys.stderr)
        return 1

    client = AllBotsClient()
    try:
        result = client.deploy_swarm(bots, coordinator=args.coordinator)
    except RuntimeError as exc:
        print(f"Swarm deployment failed: {exc}", file=sys.stderr)
        return 1

    print(json.dumps(result, indent=2))
    return 0


# ---------------------------------------------------------------------------
# Argument parser
# ---------------------------------------------------------------------------

def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="factory",
        description="Factory.ai – bot and swarm creation engine.",
    )
    sub = parser.add_subparsers(dest="command", metavar="COMMAND")
    sub.required = True

    # ---- generate ----
    gen = sub.add_parser("generate", help="Preview a bot manifest from a template.")
    gen.add_argument(
        "--template", "-t",
        required=True,
        metavar="PATH",
        help="Path to the template directory (e.g. templates/customer_support).",
    )
    gen.add_argument(
        "--name", "-n",
        required=True,
        metavar="NAME",
        help="Name to assign to the generated bot.",
    )
    gen.set_defaults(func=cmd_generate)

    # ---- deploy ----
    dep = sub.add_parser("deploy", help="Deploy a single bot to the AllBots platform.")
    dep.add_argument(
        "--template", "-t",
        required=True,
        metavar="PATH",
        help="Path to the template directory.",
    )
    dep.add_argument(
        "--name", "-n",
        default="",
        metavar="NAME",
        help="Override the bot name from the template.",
    )
    dep.add_argument(
        "--env", "-e",
        default="production",
        choices=["production", "staging", "development"],
        metavar="ENV",
        help="Target deployment environment (default: production).",
    )
    dep.set_defaults(func=cmd_deploy)

    # ---- swarm ----
    swm = sub.add_parser("swarm", help="Deploy a swarm of bots to the AllBots platform.")
    swm.add_argument(
        "--bots", "-b",
        required=True,
        metavar="NAMES",
        help="Comma-separated list of bot names to include in the swarm.",
    )
    swm.add_argument(
        "--coordinator", "-c",
        default="round-robin",
        choices=["round-robin", "priority", "least-loaded"],
        metavar="STRATEGY",
        help="Swarm coordination strategy (default: round-robin).",
    )
    swm.add_argument(
        "--env", "-e",
        default="production",
        choices=["production", "staging", "development"],
        metavar="ENV",
        help="Target deployment environment (default: production).",
    )
    swm.set_defaults(func=cmd_swarm)

    return parser


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> None:
    """Parse arguments and dispatch to the appropriate sub-command."""
    parser = _build_parser()
    args = parser.parse_args()
    sys.exit(args.func(args))


if __name__ == "__main__":
    main()
