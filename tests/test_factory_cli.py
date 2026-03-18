"""Tests for the factory CLI (factory/__main__.py)."""

from __future__ import annotations

import json
import textwrap
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from factory.__main__ import cmd_deploy, cmd_generate, cmd_swarm, main


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_args(**kwargs):
    """Return a simple namespace-like object populated with *kwargs*."""
    import argparse
    args = argparse.Namespace()
    for k, v in kwargs.items():
        setattr(args, k, v)
    return args


def _write_template(tmp_path: Path, name: str = "TestBot") -> Path:
    template_dir = tmp_path / "templates" / "test_bot"
    template_dir.mkdir(parents=True)
    (template_dir / "bot.yaml").write_text(
        textwrap.dedent(f"""\
            name: {name}
            version: "1.0.0"
            description: A test bot
            components:
              nlp:
                module: components.nlp.text_processor
            deployment:
              target: allbots
        """)
    )
    return template_dir


# ---------------------------------------------------------------------------
# cmd_generate
# ---------------------------------------------------------------------------

class TestCmdGenerate:
    def test_prints_manifest_with_custom_name(self, tmp_path, capsys):
        template_dir = _write_template(tmp_path)
        args = _make_args(template=str(template_dir), name="CustomBot")
        rc = cmd_generate(args)
        assert rc == 0
        out = capsys.readouterr().out
        data = json.loads(out)
        assert data["name"] == "CustomBot"

    def test_manifest_contains_version(self, tmp_path, capsys):
        template_dir = _write_template(tmp_path)
        args = _make_args(template=str(template_dir), name="Bot")
        cmd_generate(args)
        out = capsys.readouterr().out
        data = json.loads(out)
        assert data["version"] == "1.0.0"

    def test_missing_template_exits(self, tmp_path):
        args = _make_args(template=str(tmp_path / "nonexistent"), name="Bot")
        with pytest.raises(SystemExit):
            cmd_generate(args)


# ---------------------------------------------------------------------------
# cmd_deploy
# ---------------------------------------------------------------------------

class TestCmdDeploy:
    def test_deploy_calls_allbots_client(self, tmp_path, capsys):
        template_dir = _write_template(tmp_path)
        args = _make_args(template=str(template_dir), name="DeployBot", env="staging")

        mock_client = MagicMock()
        mock_client.deploy_bot.return_value = {"deployment_id": "d1", "status": "ok"}

        with patch("factory.__main__.AllBotsClient", return_value=mock_client):
            rc = cmd_deploy(args)

        assert rc == 0
        mock_client.deploy_bot.assert_called_once()
        out = capsys.readouterr().out
        result = json.loads(out)
        assert result["deployment_id"] == "d1"

    def test_deploy_returns_1_on_runtime_error(self, tmp_path, capsys):
        template_dir = _write_template(tmp_path)
        args = _make_args(template=str(template_dir), name="Bot", env="production")

        mock_client = MagicMock()
        mock_client.deploy_bot.side_effect = RuntimeError("API down")

        with patch("factory.__main__.AllBotsClient", return_value=mock_client):
            rc = cmd_deploy(args)

        assert rc == 1

    def test_deploy_missing_template_exits(self, tmp_path):
        args = _make_args(template=str(tmp_path / "missing"), name="Bot", env="production")
        with pytest.raises(SystemExit):
            cmd_deploy(args)


# ---------------------------------------------------------------------------
# cmd_swarm
# ---------------------------------------------------------------------------

class TestCmdSwarm:
    def test_swarm_calls_deploy_swarm(self, capsys):
        args = _make_args(bots="BotA,BotB", coordinator="round-robin", env="production")

        mock_client = MagicMock()
        mock_client.deploy_swarm.return_value = {"swarm_id": "s1"}

        with patch("factory.__main__.AllBotsClient", return_value=mock_client):
            rc = cmd_swarm(args)

        assert rc == 0
        mock_client.deploy_swarm.assert_called_once_with(
            ["BotA", "BotB"], coordinator="round-robin"
        )
        out = capsys.readouterr().out
        result = json.loads(out)
        assert result["swarm_id"] == "s1"

    def test_swarm_returns_1_on_error(self):
        args = _make_args(bots="BotA", coordinator="priority", env="staging")

        mock_client = MagicMock()
        mock_client.deploy_swarm.side_effect = RuntimeError("timeout")

        with patch("factory.__main__.AllBotsClient", return_value=mock_client):
            rc = cmd_swarm(args)

        assert rc == 1

    def test_swarm_empty_bots_returns_1(self, capsys):
        args = _make_args(bots="  ,  ", coordinator="round-robin", env="production")
        with patch("factory.__main__.AllBotsClient"):
            rc = cmd_swarm(args)
        assert rc == 1

    def test_swarm_trims_whitespace_from_bot_names(self, capsys):
        args = _make_args(bots=" BotA , BotB ", coordinator="priority", env="staging")

        mock_client = MagicMock()
        mock_client.deploy_swarm.return_value = {}

        with patch("factory.__main__.AllBotsClient", return_value=mock_client):
            cmd_swarm(args)

        call_bots = mock_client.deploy_swarm.call_args[0][0]
        assert call_bots == ["BotA", "BotB"]


# ---------------------------------------------------------------------------
# CLI integration: argument parsing via main()
# ---------------------------------------------------------------------------

class TestMainArgParsing:
    def test_no_subcommand_exits(self):
        with pytest.raises(SystemExit):
            with patch("sys.argv", ["factory"]):
                main()

    def test_generate_subcommand_dispatched(self, tmp_path, capsys):
        template_dir = _write_template(tmp_path)
        with patch(
            "sys.argv",
            ["factory", "generate", "--template", str(template_dir), "--name", "CLIBot"],
        ):
            with pytest.raises(SystemExit) as exc_info:
                main()
        assert exc_info.value.code == 0
        out = capsys.readouterr().out
        data = json.loads(out)
        assert data["name"] == "CLIBot"
