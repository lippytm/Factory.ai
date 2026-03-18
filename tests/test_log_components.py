"""Tests for ci_cd/scripts/log_components.py."""

from __future__ import annotations

import json
import textwrap

from ci_cd.scripts.log_components import build_report, extract_components


MINIMAL_MANIFEST: dict = {
    "name": "TestBot",
    "version": "1.0.0",
    "components": {
        "nlp": {"module": "components.nlp.text_processor"},
    },
    "extensions": [],
    "integrations": {
        "allbots": {"enabled": True},
    },
}


class TestExtractComponents:
    def test_extracts_core_components(self):
        result = extract_components(MINIMAL_MANIFEST)
        assert result["core_components"] == {
            "nlp": "components.nlp.text_processor"
        }

    def test_extracts_extensions_list(self):
        result = extract_components(MINIMAL_MANIFEST)
        assert result["extensions"] == []

    def test_extracts_integrations(self):
        result = extract_components(MINIMAL_MANIFEST)
        assert result["integrations"] == {"allbots": True}

    def test_missing_components_defaults_to_empty(self):
        result = extract_components({})
        assert result["core_components"] == {}

    def test_missing_extensions_defaults_to_empty_list(self):
        result = extract_components({})
        assert result["extensions"] == []

    def test_non_dict_component_uses_str(self):
        manifest = {"components": {"nlp": "some.module"}}
        result = extract_components(manifest)
        assert result["core_components"]["nlp"] == "some.module"

    def test_integration_disabled(self):
        manifest = {"integrations": {"allbots": {"enabled": False}}}
        result = extract_components(manifest)
        assert result["integrations"]["allbots"] is False

    def test_non_list_extensions_converted(self):
        manifest = {"extensions": "not-a-list"}
        result = extract_components(manifest)
        assert result["extensions"] == []


class TestBuildReport:
    def test_report_contains_generated_at(self, tmp_path):
        report = build_report(tmp_path)
        assert "generated_at" in report

    def test_report_contains_empty_templates_when_no_bot_yaml(self, tmp_path):
        report = build_report(tmp_path)
        assert report["templates"] == []

    def test_report_includes_template_entry(self, tmp_path):
        (tmp_path / "mybot").mkdir()
        bot_yaml = tmp_path / "mybot" / "bot.yaml"
        bot_yaml.write_text(
            textwrap.dedent("""\
                name: MyBot
                version: "1.0.0"
                description: Test
                components:
                  nlp:
                    module: components.nlp.text_processor
                deployment:
                  target: allbots
            """)
        )
        report = build_report(tmp_path)
        assert len(report["templates"]) == 1
        entry = report["templates"][0]
        assert entry["name"] == "MyBot"
        assert entry["version"] == "1.0.0"

    def test_report_handles_yaml_parse_error_gracefully(self, tmp_path):
        (tmp_path / "bad").mkdir()
        (tmp_path / "bad" / "bot.yaml").write_text("key: [unclosed")
        report = build_report(tmp_path)
        # Should still produce an entry, with 'unknown' name/version
        assert len(report["templates"]) == 1
        entry = report["templates"][0]
        assert entry["name"] == "unknown"

    def test_report_json_serialisable(self, tmp_path):
        report = build_report(tmp_path)
        # Should not raise
        assert json.dumps(report)
