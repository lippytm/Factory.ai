"""Tests for connection base class and individual connection types."""

import json
from io import BytesIO
from unittest.mock import MagicMock, patch
import pytest

from factory_ai.connections.base import BaseConnection
from factory_ai.connections.github import GitHubConnection
from factory_ai.connections.openai import OpenAIConnection
from factory_ai.connections.allbots import AllBotsConnection


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_response(body: dict, status: int = 200):
    """Create a mock urllib response context manager."""
    raw = json.dumps(body).encode()
    mock_resp = MagicMock()
    mock_resp.read.return_value = raw
    mock_resp.__enter__ = lambda s: s
    mock_resp.__exit__ = MagicMock(return_value=False)
    return mock_resp


# ---------------------------------------------------------------------------
# BaseConnection
# ---------------------------------------------------------------------------

class ConcreteConnection(BaseConnection):
    """Minimal concrete implementation for testing the abstract base."""

    def connect(self, **credentials) -> bool:
        self._credentials = credentials
        self._connected = True
        return True

    def validate(self) -> bool:
        return self._connected


class TestBaseConnection:
    def test_initial_state(self):
        conn = ConcreteConnection("test")
        assert conn.name == "test"
        assert conn.is_connected is False

    def test_connect_sets_connected(self):
        conn = ConcreteConnection("test")
        assert conn.connect(token="abc") is True
        assert conn.is_connected is True

    def test_disconnect_clears_state(self):
        conn = ConcreteConnection("test")
        conn.connect(token="abc")
        conn.disconnect()
        assert conn.is_connected is False
        assert conn._credentials == {}

    def test_to_dict(self):
        conn = ConcreteConnection("test")
        conn.connect()
        d = conn.to_dict()
        assert d["name"] == "test"
        assert d["type"] == "ConcreteConnection"
        assert d["connected"] is True

    def test_repr(self):
        conn = ConcreteConnection("myconn")
        assert "myconn" in repr(conn)
        assert "disconnected" in repr(conn)
        conn.connect()
        assert "connected" in repr(conn)


# ---------------------------------------------------------------------------
# GitHubConnection
# ---------------------------------------------------------------------------

class TestGitHubConnection:
    def test_connect_raises_on_empty_token(self):
        conn = GitHubConnection()
        with pytest.raises(ValueError, match="token"):
            conn.connect(token="")

    def test_connect_success(self):
        conn = GitHubConnection()
        mock_resp = _make_response({"login": "octocat"})
        with patch("urllib.request.urlopen", return_value=mock_resp):
            result = conn.connect(token="ghp_valid")
        assert result is True
        assert conn.is_connected is True
        assert conn._username == "octocat"

    def test_connect_failure_http_error(self):
        import urllib.error
        conn = GitHubConnection()
        conn._credentials = {"token": "bad"}
        with patch("urllib.request.urlopen", side_effect=urllib.error.HTTPError(
            None, 401, "Unauthorized", {}, None
        )):
            result = conn.validate()
        assert result is False
        assert conn.is_connected is False

    def test_to_dict_includes_username(self):
        conn = GitHubConnection(name="gh-work")
        mock_resp = _make_response({"login": "devuser"})
        with patch("urllib.request.urlopen", return_value=mock_resp):
            conn.connect(token="ghp_x")
        d = conn.to_dict()
        assert d["username"] == "devuser"
        assert d["name"] == "gh-work"

    def test_validate_without_credentials_returns_false(self):
        conn = GitHubConnection()
        assert conn.validate() is False


# ---------------------------------------------------------------------------
# OpenAIConnection
# ---------------------------------------------------------------------------

class TestOpenAIConnection:
    def test_connect_raises_on_empty_key(self):
        conn = OpenAIConnection()
        with pytest.raises(ValueError, match="API key"):
            conn.connect(api_key="")

    def test_connect_success(self):
        conn = OpenAIConnection()
        mock_resp = _make_response({"data": []})
        with patch("urllib.request.urlopen", return_value=mock_resp):
            result = conn.connect(api_key="sk-valid")
        assert result is True
        assert conn.is_connected is True

    def test_connect_with_organization(self):
        conn = OpenAIConnection()
        mock_resp = _make_response({"data": []})
        with patch("urllib.request.urlopen", return_value=mock_resp):
            conn.connect(api_key="sk-valid", organization="org-123")
        assert conn._organization == "org-123"
        d = conn.to_dict()
        assert d["organization"] == "org-123"

    def test_connect_failure(self):
        import urllib.error
        conn = OpenAIConnection()
        with patch("urllib.request.urlopen", side_effect=urllib.error.HTTPError(
            None, 401, "Unauthorized", {}, None
        )):
            result = conn.connect(api_key="sk-bad")
        assert result is False
        assert conn.is_connected is False

    def test_validate_without_credentials_returns_false(self):
        conn = OpenAIConnection()
        assert conn.validate() is False


# ---------------------------------------------------------------------------
# AllBotsConnection
# ---------------------------------------------------------------------------

class TestAllBotsConnection:
    def test_connect_raises_on_empty_key(self):
        conn = AllBotsConnection()
        with pytest.raises(ValueError, match="API key"):
            conn.connect(api_key="")

    def test_connect_success(self):
        conn = AllBotsConnection()
        mock_resp = _make_response({"bot_name": "MyBot"})
        with patch("urllib.request.urlopen", return_value=mock_resp):
            result = conn.connect(api_key="allbots-key-123")
        assert result is True
        assert conn.is_connected is True
        assert conn._bot_name == "MyBot"

    def test_connect_failure(self):
        import urllib.error
        conn = AllBotsConnection()
        with patch("urllib.request.urlopen", side_effect=urllib.error.HTTPError(
            None, 403, "Forbidden", {}, None
        )):
            result = conn.connect(api_key="bad-key")
        assert result is False

    def test_custom_api_url(self):
        conn = AllBotsConnection(api_url="https://custom.allbots.com/api/v2")
        assert conn.API_URL == "https://custom.allbots.com/api/v2"

    def test_to_dict_includes_bot_name(self):
        conn = AllBotsConnection(name="my-bot")
        mock_resp = _make_response({"bot_name": "FactoryBot"})
        with patch("urllib.request.urlopen", return_value=mock_resp):
            conn.connect(api_key="key")
        d = conn.to_dict()
        assert d["bot_name"] == "FactoryBot"

    def test_validate_without_credentials_returns_false(self):
        conn = AllBotsConnection()
        assert conn.validate() is False
