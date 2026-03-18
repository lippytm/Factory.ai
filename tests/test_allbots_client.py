"""Tests for integrations/allbots/client.py."""

from __future__ import annotations

import json
import urllib.error
from unittest.mock import MagicMock, patch

import pytest

from integrations.allbots.client import AllBotsClient


class TestAllBotsClientInit:
    def test_api_key_from_argument(self):
        client = AllBotsClient(api_key="test-key")
        assert client.api_key == "test-key"

    def test_api_key_from_env(self, monkeypatch):
        monkeypatch.setenv("ALLBOTS_API_KEY", "env-key")
        client = AllBotsClient()
        assert client.api_key == "env-key"

    def test_default_base_url(self):
        client = AllBotsClient(api_key="k")
        assert client.base_url == "https://api.allbots.com/v1"

    def test_custom_base_url_strips_trailing_slash(self):
        client = AllBotsClient(api_key="k", base_url="https://staging.example.com/")
        assert client.base_url == "https://staging.example.com"

    def test_missing_api_key_defaults_to_empty_string(self, monkeypatch):
        monkeypatch.delenv("ALLBOTS_API_KEY", raising=False)
        client = AllBotsClient()
        assert client.api_key == ""


class TestAllBotsClientPost:
    """Test the _post method using urllib mock."""

    def _make_response(self, body: dict, status: int = 200) -> MagicMock:
        """Return a mock urllib response context manager."""
        raw = json.dumps(body).encode()
        mock_resp = MagicMock()
        mock_resp.read.return_value = raw
        mock_resp.__enter__ = lambda s: s
        mock_resp.__exit__ = MagicMock(return_value=False)
        return mock_resp

    def test_post_sends_correct_url(self):
        client = AllBotsClient(api_key="key", base_url="https://api.example.com")
        mock_resp = self._make_response({"status": "ok"})
        with patch("urllib.request.urlopen", return_value=mock_resp) as mock_open:
            client._post("/test/path", {"k": "v"})
            call_args = mock_open.call_args[0][0]
            assert call_args.full_url == "https://api.example.com/test/path"

    def test_post_sends_json_body(self):
        client = AllBotsClient(api_key="key")
        mock_resp = self._make_response({"ok": True})
        with patch("urllib.request.urlopen", return_value=mock_resp) as mock_open:
            client._post("/bots/deploy", {"name": "MyBot"})
            req = mock_open.call_args[0][0]
            assert json.loads(req.data) == {"name": "MyBot"}

    def test_post_sets_content_type_header(self):
        client = AllBotsClient(api_key="key")
        mock_resp = self._make_response({"ok": True})
        with patch("urllib.request.urlopen", return_value=mock_resp) as mock_open:
            client._post("/test", {})
            req = mock_open.call_args[0][0]
            assert req.get_header("Content-type") == "application/json"

    def test_post_sets_authorization_header(self):
        client = AllBotsClient(api_key="my-secret-key")
        mock_resp = self._make_response({"ok": True})
        with patch("urllib.request.urlopen", return_value=mock_resp) as mock_open:
            client._post("/test", {})
            req = mock_open.call_args[0][0]
            assert req.get_header("Authorization") == "Bearer my-secret-key"

    def test_post_returns_parsed_json(self):
        client = AllBotsClient(api_key="key")
        mock_resp = self._make_response({"deployment_id": "abc123"})
        with patch("urllib.request.urlopen", return_value=mock_resp):
            result = client._post("/bots/deploy", {})
        assert result == {"deployment_id": "abc123"}

    def test_post_raises_runtime_error_on_http_error(self):
        client = AllBotsClient(api_key="key")
        http_error = urllib.error.HTTPError(
            url="https://api.allbots.com/v1/bots/deploy",
            code=403,
            msg="Forbidden",
            hdrs=None,  # type: ignore[arg-type]
            fp=None,
        )
        with patch("urllib.request.urlopen", side_effect=http_error):
            with pytest.raises(RuntimeError, match="403"):
                client._post("/bots/deploy", {})


class TestAllBotsClientPublicMethods:
    """Verify public methods delegate to _post with the correct arguments."""

    def _patched_client(self, return_value: dict) -> AllBotsClient:
        client = AllBotsClient(api_key="key")
        client._post = MagicMock(return_value=return_value)  # type: ignore[method-assign]
        return client

    def test_deploy_bot_calls_bots_deploy(self):
        client = self._patched_client({"status": "deployed"})
        manifest = {"name": "Bot", "version": "1.0"}
        result = client.deploy_bot(manifest)
        client._post.assert_called_once_with("/bots/deploy", body=manifest)
        assert result == {"status": "deployed"}

    def test_deploy_swarm_calls_swarms_create(self):
        client = self._patched_client({"swarm_id": "s1"})
        result = client.deploy_swarm(["BotA", "BotB"], coordinator="priority")
        client._post.assert_called_once_with(
            "/swarms/create",
            body={"bots": ["BotA", "BotB"], "coordinator": "priority"},
        )
        assert result == {"swarm_id": "s1"}

    def test_deploy_swarm_default_coordinator(self):
        client = self._patched_client({})
        client.deploy_swarm(["BotA"])
        _, kwargs = client._post.call_args
        assert kwargs["body"]["coordinator"] == "round-robin"

    def test_publish_event_calls_events_publish(self):
        client = self._patched_client({"ok": True})
        result = client.publish_event("my-queue", {"type": "click"})
        client._post.assert_called_once_with(
            "/events/publish",
            body={"queue": "my-queue", "event": {"type": "click"}},
        )
        assert result == {"ok": True}
