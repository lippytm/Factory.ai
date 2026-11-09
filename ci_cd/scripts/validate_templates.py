#!/usr/bin/env python3
"""
validate_templates.py – Factory.ai template validation script.

Scans every ``bot.yaml`` found under the ``templates/`` directory and
validates that each manifest contains the required top-level keys.  Exits
with a non-zero status code if any manifest is invalid so that CI can
catch broken templates early.

Usage::

    python ci_cd/scripts/validate_templates.py

"""

from __future__ import annotations

import sys
from pathlib import Path

import yaml

REQUIRED_KEYS = {"name", "version", "description", "components", "deployment"}
# Manifests marked ``status: architecture_only`` describe a design that is not
# yet buildable. They are checked against their own schema and must not claim
# a deployment, so they cannot slip into production unreviewed.
ARCHITECTURE_REQUIRED_KEYS = {"name", "template_version", "purpose", "agents", "pipeline"}
TEMPLATES_ROOT = Path(__file__).resolve().parents[2] / "templates"


def validate_manifest(path: Path) -> list[str]:
    """Return a list of error strings for *path*; empty list means valid."""
    errors: list[str] = []
    try:
        with path.open() as fh:
            data = yaml.safe_load(fh)
    except yaml.YAMLError as exc:
        return [f"YAML parse error: {exc}"]

    if not isinstance(data, dict):
        return ["Manifest must be a YAML mapping at the top level."]

    if data.get("status") == "architecture_only":
        return validate_architecture_manifest(data)

    missing = REQUIRED_KEYS - data.keys()
    if missing:
        errors.append(f"Missing required keys: {sorted(missing)}")

    name = data.get("name", "")
    if not isinstance(name, str) or not name.strip():
        errors.append("'name' must be a non-empty string.")

    version = data.get("version", "")
    if not isinstance(version, str) or not version.strip():
        errors.append("'version' must be a non-empty string.")

    components = data.get("components")
    if not isinstance(components, dict) or not components:
        errors.append("'components' must be a non-empty mapping.")

    deployment = data.get("deployment")
    if not isinstance(deployment, dict) or "target" not in deployment:
        errors.append("'deployment' must be a mapping containing 'target'.")

    return errors


def validate_architecture_manifest(data: dict) -> list[str]:
    """Validate a design-only manifest; empty list means valid."""
    errors: list[str] = []
    missing = ARCHITECTURE_REQUIRED_KEYS - data.keys()
    if missing:
        errors.append(f"Missing required architecture keys: {sorted(missing)}")
    for key in ("name", "template_version", "purpose"):
        value = data.get(key)
        if key in data and (not isinstance(value, str) or not value.strip()):
            errors.append(f"'{key}' must be a non-empty string.")
    agents = data.get("agents")
    if "agents" in data and (not isinstance(agents, list) or not agents
                             or not all(isinstance(a, dict) and a.get("id") for a in agents)):
        errors.append("'agents' must be a non-empty list of mappings with an 'id'.")
    pipeline = data.get("pipeline")
    if "pipeline" in data and (not isinstance(pipeline, list) or not pipeline):
        errors.append("'pipeline' must be a non-empty list.")
    if "deployment" in data:
        errors.append("Architecture-only manifests must not define 'deployment'.")
    claims = data.get("claims") or {}
    if isinstance(claims, dict) and claims.get("deployed_production_service"):
        errors.append("Architecture-only manifests must not claim a deployed production service.")
    return errors


def main() -> int:
    manifests = sorted(TEMPLATES_ROOT.rglob("bot.yaml"))
    if not manifests:
        print(f"No bot.yaml files found under {TEMPLATES_ROOT}", file=sys.stderr)
        return 1

    all_valid = True
    for manifest_path in manifests:
        relative = manifest_path.relative_to(TEMPLATES_ROOT.parent)
        errors = validate_manifest(manifest_path)
        if errors:
            all_valid = False
            print(f"✗ {relative}")
            for err in errors:
                print(f"    - {err}")
        else:
            print(f"✓ {relative}")

    if not all_valid:
        print("\nTemplate validation FAILED.", file=sys.stderr)
        return 1

    print("\nAll templates are valid.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
