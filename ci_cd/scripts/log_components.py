#!/usr/bin/env python3
"""
log_components.py – Factory.ai component transparency logger.

Scans every ``bot.yaml`` found under the ``templates/`` directory and
emits a structured report of which components are used by each template.
The report is written to stdout (and optionally to a file) so that CI
pipelines can archive it as a build artifact for auditing and transparency.

Usage::

    # Print to stdout
    python ci_cd/scripts/log_components.py

    # Write to a file
    python ci_cd/scripts/log_components.py --output component_log.json

"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import yaml

TEMPLATES_ROOT = Path(__file__).resolve().parents[2] / "templates"


def extract_components(manifest: dict) -> dict:
    """Return a summary of components declared in *manifest*."""
    components = manifest.get("components", {})
    extensions = manifest.get("extensions", [])
    integrations = manifest.get("integrations", {})
    brain_kit = manifest.get("brain_kit", {})

    component_summary: dict = {
        "core_components": {
            name: cfg.get("module", "unknown") if isinstance(cfg, dict) else str(cfg)
            for name, cfg in components.items()
        },
        "extensions": list(extensions) if isinstance(extensions, list) else [],
        "integrations": {
            name: cfg.get("enabled", False) if isinstance(cfg, dict) else False
            for name, cfg in integrations.items()
        },
    }

    if brain_kit:
        component_summary["brain_kit"] = {
            "module": brain_kit.get("module", "unknown"),
            "enabled": True,
        }

    return component_summary


def build_report(templates_root: Path) -> dict:
    """Walk *templates_root* and build a full component report."""
    manifests = sorted(templates_root.rglob("bot.yaml"))
    report: dict = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "templates": [],
    }

    for manifest_path in manifests:
        try:
            with manifest_path.open() as fh:
                data = yaml.safe_load(fh) or {}
        except yaml.YAMLError as exc:
            data = {"_parse_error": str(exc)}

        relative = str(manifest_path.relative_to(templates_root.parent))
        report["templates"].append(
            {
                "path": relative,
                "name": data.get("name", "unknown"),
                "version": data.get("version", "unknown"),
                "components": extract_components(data),
            }
        )

    return report


def main() -> int:
    parser = argparse.ArgumentParser(description="Log Factory.ai template components.")
    parser.add_argument(
        "--output", "-o",
        metavar="FILE",
        help="Write the JSON report to FILE instead of stdout.",
    )
    args = parser.parse_args()

    report = build_report(TEMPLATES_ROOT)
    output = json.dumps(report, indent=2)

    if args.output:
        Path(args.output).write_text(output)
        print(f"Component log written to {args.output}")
    else:
        print(output)

    return 0


if __name__ == "__main__":
    sys.exit(main())
