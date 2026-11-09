"""Tests for ci_cd/scripts/validate_templates.py."""

from __future__ import annotations

import textwrap
from pathlib import Path

from ci_cd.scripts.validate_templates import validate_manifest


def _write_yaml(tmp_path: Path, content: str) -> Path:
    """Write *content* to a bot.yaml inside *tmp_path* and return the path."""
    path = tmp_path / "bot.yaml"
    path.write_text(content)
    return path


VALID_MANIFEST = textwrap.dedent("""\
    name: TestBot
    version: "1.0.0"
    description: A test bot
    components:
      nlp:
        module: components.nlp.text_processor
    deployment:
      target: allbots
""")


class TestValidateManifest:
    def test_valid_manifest_returns_no_errors(self, tmp_path):
        path = _write_yaml(tmp_path, VALID_MANIFEST)
        assert validate_manifest(path) == []

    def test_missing_required_key_name(self, tmp_path):
        content = VALID_MANIFEST.replace("name: TestBot\n", "")
        path = _write_yaml(tmp_path, content)
        errors = validate_manifest(path)
        assert any("name" in e.lower() or "Missing" in e for e in errors)

    def test_missing_required_key_version(self, tmp_path):
        content = VALID_MANIFEST.replace('version: "1.0.0"\n', "")
        path = _write_yaml(tmp_path, content)
        errors = validate_manifest(path)
        assert any("version" in e.lower() or "Missing" in e for e in errors)

    def test_missing_required_key_deployment(self, tmp_path):
        content = VALID_MANIFEST.replace("deployment:\n  target: allbots\n", "")
        path = _write_yaml(tmp_path, content)
        errors = validate_manifest(path)
        assert any("deployment" in e.lower() or "Missing" in e for e in errors)

    def test_missing_required_key_components(self, tmp_path):
        content = VALID_MANIFEST.replace(
            "components:\n  nlp:\n    module: components.nlp.text_processor\n", ""
        )
        path = _write_yaml(tmp_path, content)
        errors = validate_manifest(path)
        assert any("components" in e.lower() or "Missing" in e for e in errors)

    def test_empty_name_is_invalid(self, tmp_path):
        content = VALID_MANIFEST.replace("name: TestBot", "name: ''")
        path = _write_yaml(tmp_path, content)
        errors = validate_manifest(path)
        assert any("name" in e.lower() for e in errors)

    def test_non_string_name_is_invalid(self, tmp_path):
        content = VALID_MANIFEST.replace("name: TestBot", "name: 123")
        path = _write_yaml(tmp_path, content)
        errors = validate_manifest(path)
        # YAML loads 123 as an int, so 'name' validation should flag it
        assert any("name" in e.lower() for e in errors)

    def test_empty_components_is_invalid(self, tmp_path):
        content = VALID_MANIFEST.replace(
            "components:\n  nlp:\n    module: components.nlp.text_processor\n",
            "components: {}\n",
        )
        path = _write_yaml(tmp_path, content)
        errors = validate_manifest(path)
        assert any("components" in e.lower() for e in errors)

    def test_deployment_missing_target_is_invalid(self, tmp_path):
        content = VALID_MANIFEST.replace(
            "deployment:\n  target: allbots\n",
            "deployment:\n  replicas: 1\n",
        )
        path = _write_yaml(tmp_path, content)
        errors = validate_manifest(path)
        assert any("deployment" in e.lower() or "target" in e.lower() for e in errors)

    def test_yaml_syntax_error_returns_error(self, tmp_path):
        path = tmp_path / "bot.yaml"
        path.write_text("key: [unclosed")
        errors = validate_manifest(path)
        assert len(errors) == 1
        assert "YAML" in errors[0] or "parse" in errors[0].lower()

    def test_non_mapping_top_level_is_invalid(self, tmp_path):
        path = _write_yaml(tmp_path, "- item1\n- item2\n")
        errors = validate_manifest(path)
        assert any("mapping" in e.lower() for e in errors)


ARCHITECTURE_MANIFEST = textwrap.dedent("""\
    template_version: "0.3"
    name: design-only-factory
    status: architecture_only
    purpose: Describe a pipeline that is not built yet.
    claims:
      deployed_production_service: false
    agents:
      - id: intake-validator
        role: Validate input
    pipeline:
      - intake_validation
""")


class TestArchitectureOnlyManifest:
    def test_valid_architecture_manifest(self, tmp_path):
        assert validate_manifest(_write_yaml(tmp_path, ARCHITECTURE_MANIFEST)) == []

    def test_architecture_manifest_must_not_deploy(self, tmp_path):
        content = ARCHITECTURE_MANIFEST + "deployment:\n  target: allbots\n"
        errors = validate_manifest(_write_yaml(tmp_path, content))
        assert any("must not define 'deployment'" in e for e in errors)

    def test_architecture_manifest_must_not_claim_production(self, tmp_path):
        content = ARCHITECTURE_MANIFEST.replace("deployed_production_service: false",
                                                "deployed_production_service: true")
        errors = validate_manifest(_write_yaml(tmp_path, content))
        assert any("production service" in e for e in errors)

    def test_architecture_manifest_requires_agents_and_pipeline(self, tmp_path):
        content = ARCHITECTURE_MANIFEST.replace("pipeline:\n  - intake_validation\n", "")
        content = content.replace("agents:\n  - id: intake-validator\n    role: Validate input\n",
                                  "agents: []\n")
        errors = validate_manifest(_write_yaml(tmp_path, content))
        assert any("'pipeline'" in e for e in errors)
        assert any("'agents'" in e for e in errors)

    def test_repository_templates_are_valid(self):
        from ci_cd.scripts.validate_templates import main
        assert main() == 0
