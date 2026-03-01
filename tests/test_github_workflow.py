"""
Tests for GitHubWorkflow.

All HTTP calls are intercepted with unittest.mock so no real network
requests or credentials are required.
"""

import json
from unittest.mock import MagicMock, patch

import pytest

from workflows.github_workflow import GitHubWorkflow


@pytest.fixture
def workflow():
    return GitHubWorkflow(token="test-token")


def _mock_response(data, status_code=200):
    mock = MagicMock()
    mock.status_code = status_code
    mock.json.return_value = data
    mock.raise_for_status.return_value = None
    return mock


class TestGitHubWorkflow:
    def test_init_requires_token(self):
        with pytest.raises(ValueError, match="GitHub token"):
            with patch.dict("os.environ", {}, clear=True):
                GitHubWorkflow(token=None)

    def test_init_reads_env_token(self):
        with patch.dict("os.environ", {"GITHUB_TOKEN": "env-token"}):
            wf = GitHubWorkflow()
        assert wf.token == "env-token"

    def test_list_repos(self, workflow):
        repos = [{"name": "repo1"}, {"name": "repo2"}]
        with patch.object(
            workflow.session, "get", return_value=_mock_response(repos)
        ) as mock_get:
            result = workflow.list_repos()
        assert result == repos
        mock_get.assert_called_once()

    def test_list_repos_for_org(self, workflow):
        repos = [{"name": "org-repo"}]
        with patch.object(
            workflow.session, "get", return_value=_mock_response(repos)
        ) as mock_get:
            result = workflow.list_repos(org="myorg")
        assert "orgs/myorg" in mock_get.call_args[0][0]
        assert result == repos

    def test_get_repo(self, workflow):
        repo_data = {"id": 1, "name": "Factory.ai"}
        with patch.object(
            workflow.session, "get", return_value=_mock_response(repo_data)
        ):
            result = workflow.get_repo("lippytm", "Factory.ai")
        assert result["name"] == "Factory.ai"

    def test_list_issues(self, workflow):
        issues = [{"number": 1, "title": "Bug"}]
        with patch.object(
            workflow.session, "get", return_value=_mock_response(issues)
        ):
            result = workflow.list_issues("owner", "repo")
        assert len(result) == 1

    def test_create_issue(self, workflow):
        new_issue = {"number": 42, "title": "New issue"}
        with patch.object(
            workflow.session, "post", return_value=_mock_response(new_issue)
        ):
            result = workflow.create_issue("owner", "repo", "New issue")
        assert result["number"] == 42

    def test_list_pull_requests(self, workflow):
        prs = [{"number": 10, "title": "PR"}]
        with patch.object(
            workflow.session, "get", return_value=_mock_response(prs)
        ):
            result = workflow.list_pull_requests("owner", "repo")
        assert len(result) == 1

    def test_create_webhook(self, workflow):
        hook = {"id": 99, "config": {"url": "https://example.com/hook"}}
        with patch.object(
            workflow.session, "post", return_value=_mock_response(hook)
        ):
            result = workflow.create_webhook(
                "owner", "repo", "https://example.com/hook"
            )
        assert result["id"] == 99

    def test_run(self, workflow):
        repo_data = {"id": 1}
        issues = []
        prs = []

        responses = [
            _mock_response(repo_data),
            _mock_response(issues),
            _mock_response(prs),
        ]
        with patch.object(workflow.session, "get", side_effect=responses):
            result = workflow.run("owner", "repo")
        assert "repo" in result
        assert "issues" in result
        assert "pull_requests" in result
