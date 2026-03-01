"""Command-line interface for Factory.ai connection workflows."""

import argparse
import json
import sys


def _create(args):
    from factory_ai.workflow import ConnectionWorkflow

    wf = ConnectionWorkflow()
    credentials = dict(pair.split("=", 1) for pair in (args.credentials or []))
    try:
        conn = wf.create(args.service, name=args.name, **credentials)
        print(f"✓ Connected: {conn}")
        print(json.dumps(conn.to_dict(), indent=2))
    except (ValueError, ConnectionError) as exc:
        print(f"✗ {exc}", file=sys.stderr)
        sys.exit(1)


def _list(args):
    from factory_ai.workflow import ConnectionWorkflow

    wf = ConnectionWorkflow()
    connections = wf.list_connections()
    if not connections:
        print("No saved connections.")
        return
    for entry in connections:
        status = "connected" if entry.get("connected") else "disconnected"
        print(f"  [{status}] {entry['name']} ({entry['type']})")


def _remove(args):
    from factory_ai.workflow import ConnectionWorkflow

    wf = ConnectionWorkflow()
    if wf.remove(args.name):
        print(f"✓ Removed connection: {args.name}")
    else:
        print(f"No connection named {args.name!r} found.", file=sys.stderr)
        sys.exit(1)


def _services(_args):
    from factory_ai.workflow import ConnectionWorkflow

    print("Supported services:")
    for svc in ConnectionWorkflow.supported_services():
        print(f"  - {svc}")


def main(argv=None):
    parser = argparse.ArgumentParser(
        prog="factory-ai",
        description="Factory.ai — manage connection workflows to GitHub, ChatGPT, AllBots, and more.",
    )
    sub = parser.add_subparsers(dest="command", metavar="COMMAND")
    sub.required = True

    # create
    p_create = sub.add_parser("create", help="Create a new connection.")
    p_create.add_argument("service", help="Service to connect to (e.g. github, openai, allbots).")
    p_create.add_argument("--name", help="Friendly name for the connection.")
    p_create.add_argument(
        "credentials",
        nargs="*",
        metavar="KEY=VALUE",
        help="Credential key-value pairs (e.g. token=ghp_xxx or api_key=sk-xxx).",
    )
    p_create.set_defaults(func=_create)

    # list
    p_list = sub.add_parser("list", help="List saved connections.")
    p_list.set_defaults(func=_list)

    # remove
    p_remove = sub.add_parser("remove", help="Remove a saved connection.")
    p_remove.add_argument("name", help="Name of the connection to remove.")
    p_remove.set_defaults(func=_remove)

    # services
    p_services = sub.add_parser("services", help="List supported services.")
    p_services.set_defaults(func=_services)

    args = parser.parse_args(argv)
    args.func(args)


if __name__ == "__main__":
    main()
