"""Tests for ConnectionWorkflow and ConfigManager."""

import json
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch
import pytest

from factory_ai.workflow import ConnectionWorkflow
from factory_ai.config import ConfigManager


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_response(body: dict):
    raw = json.dumps(body).encode()
    mock_resp = MagicMock()
    mock_resp.read.return_value = raw
    mock_resp.__enter__ = lambda s: s
    mock_resp.__exit__ = MagicMock(return_value=False)
    return mock_resp


# ---------------------------------------------------------------------------
# ConfigManager
# ---------------------------------------------------------------------------

class TestConfigManager:
    def setup_method(self):
        self._tmp = tempfile.NamedTemporaryFile(suffix=".json", delete=False)
        self._tmp.close()
        self.cfg = ConfigManager(Path(self._tmp.name))
        # Start with empty config
        Path(self._tmp.name).unlink()

    def test_list_empty(self):
        assert self.cfg.list_connections() == []

    def test_save_and_get(self):
        self.cfg.save_connection({"name": "gh", "type": "GitHubConnection", "connected": True})
        entry = self.cfg.get_connection("gh")
        assert entry is not None
        assert entry["name"] == "gh"

    def test_save_overwrites(self):
        self.cfg.save_connection({"name": "gh", "type": "GitHubConnection", "connected": False})
        self.cfg.save_connection({"name": "gh", "type": "GitHubConnection", "connected": True})
        entry = self.cfg.get_connection("gh")
        assert entry["connected"] is True

    def test_list_connections(self):
        self.cfg.save_connection({"name": "a", "type": "T", "connected": True})
        self.cfg.save_connection({"name": "b", "type": "T", "connected": False})
        names = {e["name"] for e in self.cfg.list_connections()}
        assert names == {"a", "b"}

    def test_remove_existing(self):
        self.cfg.save_connection({"name": "x", "type": "T", "connected": True})
        assert self.cfg.remove_connection("x") is True
        assert self.cfg.get_connection("x") is None

    def test_remove_nonexistent(self):
        assert self.cfg.remove_connection("does-not-exist") is False

    def test_get_nonexistent(self):
        assert self.cfg.get_connection("nope") is None


# ---------------------------------------------------------------------------
# ConnectionWorkflow
# ---------------------------------------------------------------------------

class TestConnectionWorkflow:
    def setup_method(self):
        self._tmp = tempfile.NamedTemporaryFile(suffix=".json", delete=False)
        self._tmp.close()
        config_path = Path(self._tmp.name)
        config_path.unlink()
        self.wf = ConnectionWorkflow(config_path=config_path)

    def test_supported_services(self):
        services = ConnectionWorkflow.supported_services()
        assert "github" in services
        assert "openai" in services
        assert "chatgpt" in services
        assert "allbots" in services

    def test_create_github(self):
        mock_resp = _make_response({"login": "user1"})
        with patch("urllib.request.urlopen", return_value=mock_resp):
            conn = self.wf.create("github", token="ghp_test")
        assert conn.is_connected is True
        assert self.wf.get("github") is conn

    def test_create_openai(self):
        mock_resp = _make_response({"data": []})
        with patch("urllib.request.urlopen", return_value=mock_resp):
            conn = self.wf.create("openai", api_key="sk-test")
        assert conn.is_connected is True

    def test_create_chatgpt_alias(self):
        mock_resp = _make_response({"data": []})
        with patch("urllib.request.urlopen", return_value=mock_resp):
            conn = self.wf.create("chatgpt", api_key="sk-test")
        assert conn.is_connected is True

    def test_create_allbots(self):
        mock_resp = _make_response({"bot_name": "TestBot"})
        with patch("urllib.request.urlopen", return_value=mock_resp):
            conn = self.wf.create("allbots", api_key="ab-key")
        assert conn.is_connected is True

    def test_create_unknown_service_raises(self):
        with pytest.raises(ValueError, match="Unknown service"):
            self.wf.create("fakeservice", api_key="x")

    def test_create_failed_connection_raises(self):
        import urllib.error
        with patch("urllib.request.urlopen", side_effect=urllib.error.HTTPError(
            None, 401, "Unauthorized", {}, None
        )):
            with pytest.raises(ConnectionError):
                self.wf.create("github", token="bad")

    def test_list_connections_after_create(self):
        mock_resp = _make_response({"login": "user1"})
        with patch("urllib.request.urlopen", return_value=mock_resp):
            self.wf.create("github", token="ghp_test")
        connections = self.wf.list_connections()
        assert len(connections) == 1
        assert connections[0]["name"] == "github"

    def test_remove_connection(self):
        mock_resp = _make_response({"login": "user1"})
        with patch("urllib.request.urlopen", return_value=mock_resp):
            self.wf.create("github", token="ghp_test")
        assert self.wf.remove("github") is True
        assert self.wf.get("github") is None
        assert self.wf.list_connections() == []

    def test_remove_nonexistent_returns_false(self):
        assert self.wf.remove("nope") is False

    def test_create_with_custom_name(self):
        mock_resp = _make_response({"login": "user1"})
        with patch("urllib.request.urlopen", return_value=mock_resp):
            conn = self.wf.create("github", name="work-gh", token="ghp_test")
        assert conn.name == "work-gh"
        assert self.wf.get("work-gh") is conn
