"""Tests for github_connector.py."""

import pytest
import requests
import requests.models

from github_connector import GitHubConnector


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_response(json_data, *, status_code=200, link_header=""):
    """Build a minimal requests.Response-like object for mocking."""
    response = requests.models.Response()
    response.status_code = status_code
    response._content = __import__("json").dumps(json_data).encode()
    if link_header:
        response.headers["Link"] = link_header
    return response


_REPO_1 = {
    "full_name": "lippytm/repo-new",
    "html_url": "https://github.com/lippytm/repo-new",
    "private": False,
    "created_at": "2026-03-01T00:00:00Z",
    "updated_at": "2026-03-01T00:00:00Z",
    "default_branch": "main",
}
_REPO_2 = {
    "full_name": "lippytm/repo-old",
    "html_url": "https://github.com/lippytm/repo-old",
    "private": True,
    "created_at": "2025-01-01T00:00:00Z",
    "updated_at": "2025-06-01T00:00:00Z",
    "default_branch": "main",
}


# ---------------------------------------------------------------------------
# Initialisation
# ---------------------------------------------------------------------------


def test_raises_without_token(monkeypatch):
    monkeypatch.delenv("GITHUB_TOKEN", raising=False)
    with pytest.raises(ValueError, match="GitHub token"):
        GitHubConnector()


def test_uses_env_token(monkeypatch):
    monkeypatch.setenv("GITHUB_TOKEN", "ghp_test_token")
    connector = GitHubConnector()
    assert connector.token == "ghp_test_token"


def test_explicit_token_takes_precedence(monkeypatch):
    monkeypatch.setenv("GITHUB_TOKEN", "ghp_env")
    connector = GitHubConnector(token="ghp_explicit")
    assert connector.token == "ghp_explicit"


# ---------------------------------------------------------------------------
# _next_page_url
# ---------------------------------------------------------------------------


def test_next_page_url_present():
    response = _make_response(
        [],
        link_header='<https://api.github.com/user/repos?page=2>; rel="next", '
        '<https://api.github.com/user/repos?page=5>; rel="last"',
    )
    assert (
        GitHubConnector._next_page_url(response)
        == "https://api.github.com/user/repos?page=2"
    )


def test_next_page_url_absent():
    response = _make_response(
        [],
        link_header='<https://api.github.com/user/repos?page=1>; rel="prev"',
    )
    assert GitHubConnector._next_page_url(response) is None


def test_next_page_url_no_link_header():
    response = _make_response([])
    assert GitHubConnector._next_page_url(response) is None


# ---------------------------------------------------------------------------
# get_all_repositories — single page
# ---------------------------------------------------------------------------


def test_get_all_repositories_single_page(monkeypatch):
    connector = GitHubConnector(token="ghp_test")
    responses = [_make_response([_REPO_1, _REPO_2])]

    def fake_get(url, params=None, **kwargs):
        return responses.pop(0)

    monkeypatch.setattr(connector.session, "get", fake_get)
    repos = connector.get_all_repositories()
    assert len(repos) == 2
    assert repos[0]["full_name"] == "lippytm/repo-new"


# ---------------------------------------------------------------------------
# get_all_repositories — pagination (two pages)
# ---------------------------------------------------------------------------


def test_get_all_repositories_pagination(monkeypatch):
    connector = GitHubConnector(token="ghp_test")
    page1 = _make_response(
        [_REPO_1],
        link_header='<https://api.github.com/user/repos?page=2>; rel="next"',
    )
    page2 = _make_response([_REPO_2])

    calls = iter([page1, page2])

    def fake_get(url, params=None, **kwargs):
        return next(calls)

    monkeypatch.setattr(connector.session, "get", fake_get)
    repos = connector.get_all_repositories()
    assert len(repos) == 2


# ---------------------------------------------------------------------------
# get_all_repositories — newest repos are first (sort=created, direction=desc)
# ---------------------------------------------------------------------------


def test_newest_repositories_appear_first(monkeypatch):
    connector = GitHubConnector(token="ghp_test")
    # API returns newest first (sort=created desc — the default)
    monkeypatch.setattr(
        connector.session,
        "get",
        lambda url, params=None, **kw: _make_response([_REPO_1, _REPO_2]),
    )
    repos = connector.get_all_repositories()
    assert repos[0]["created_at"] > repos[1]["created_at"]


# ---------------------------------------------------------------------------
# connect
# ---------------------------------------------------------------------------


def test_connect_returns_expected_fields(monkeypatch):
    connector = GitHubConnector(token="ghp_test")
    monkeypatch.setattr(
        connector.session,
        "get",
        lambda url, params=None, **kw: _make_response([_REPO_1]),
    )
    connected = connector.connect()
    assert len(connected) == 1
    repo = connected[0]
    assert repo["full_name"] == "lippytm/repo-new"
    assert repo["html_url"] == "https://github.com/lippytm/repo-new"
    assert repo["private"] is False
    assert "created_at" in repo
    assert "updated_at" in repo
    assert "default_branch" in repo


def test_connect_empty_account(monkeypatch):
    connector = GitHubConnector(token="ghp_test")
    monkeypatch.setattr(
        connector.session,
        "get",
        lambda url, params=None, **kw: _make_response([]),
    )
    assert connector.connect() == []
