"""
GitHub Connectivity Workflow
Handles interactions with the GitHub API: repositories, issues, pull requests,
commits, and webhooks.
"""

import os
import logging
import requests

logger = logging.getLogger(__name__)

GITHUB_API_BASE = "https://api.github.com"


class GitHubWorkflow:
    """Workflow for GitHub API connectivity and automation."""

    def __init__(self, token: str | None = None):
        """
        Initialize the GitHub workflow.

        Args:
            token: GitHub personal access token. Falls back to the
                   GITHUB_TOKEN environment variable when not provided.
        """
        self.token = token or os.environ.get("GITHUB_TOKEN")
        if not self.token:
            raise ValueError(
                "A GitHub token is required. Set the GITHUB_TOKEN "
                "environment variable or pass token= explicitly."
            )
        self.session = requests.Session()
        self.session.headers.update(
            {
                "Authorization": f"Bearer {self.token}",
                "Accept": "application/vnd.github+json",
                "X-GitHub-Api-Version": "2022-11-28",
            }
        )

    # ------------------------------------------------------------------
    # Repository helpers
    # ------------------------------------------------------------------

    def list_repos(self, org: str | None = None) -> list[dict]:
        """
        List repositories for the authenticated user or a given organisation.

        Args:
            org: Organisation name. When omitted, returns the authenticated
                 user's repositories.

        Returns:
            List of repository objects returned by the API.
        """
        if org:
            url = f"{GITHUB_API_BASE}/orgs/{org}/repos"
        else:
            url = f"{GITHUB_API_BASE}/user/repos"
        response = self.session.get(url, params={"per_page": 100})
        response.raise_for_status()
        repos = response.json()
        logger.info("Found %d repositories.", len(repos))
        return repos

    def get_repo(self, owner: str, repo: str) -> dict:
        """
        Fetch details for a single repository.

        Args:
            owner: Repository owner (user or organisation).
            repo: Repository name.

        Returns:
            Repository object returned by the API.
        """
        url = f"{GITHUB_API_BASE}/repos/{owner}/{repo}"
        response = self.session.get(url)
        response.raise_for_status()
        return response.json()

    # ------------------------------------------------------------------
    # Issue helpers
    # ------------------------------------------------------------------

    def list_issues(self, owner: str, repo: str, state: str = "open") -> list[dict]:
        """
        List issues for a repository.

        Args:
            owner: Repository owner.
            repo: Repository name.
            state: Issue state – ``"open"``, ``"closed"``, or ``"all"``.

        Returns:
            List of issue objects.
        """
        url = f"{GITHUB_API_BASE}/repos/{owner}/{repo}/issues"
        response = self.session.get(url, params={"state": state, "per_page": 100})
        response.raise_for_status()
        issues = response.json()
        logger.info("Found %d issues (%s).", len(issues), state)
        return issues

    def create_issue(self, owner: str, repo: str, title: str, body: str = "") -> dict:
        """
        Create a new issue.

        Args:
            owner: Repository owner.
            repo: Repository name.
            title: Issue title.
            body: Optional issue body / description.

        Returns:
            Created issue object.
        """
        url = f"{GITHUB_API_BASE}/repos/{owner}/{repo}/issues"
        payload = {"title": title, "body": body}
        response = self.session.post(url, json=payload)
        response.raise_for_status()
        issue = response.json()
        logger.info("Created issue #%d: %s", issue["number"], title)
        return issue

    # ------------------------------------------------------------------
    # Pull-request helpers
    # ------------------------------------------------------------------

    def list_pull_requests(
        self, owner: str, repo: str, state: str = "open"
    ) -> list[dict]:
        """
        List pull requests for a repository.

        Args:
            owner: Repository owner.
            repo: Repository name.
            state: PR state – ``"open"``, ``"closed"``, or ``"all"``.

        Returns:
            List of pull-request objects.
        """
        url = f"{GITHUB_API_BASE}/repos/{owner}/{repo}/pulls"
        response = self.session.get(url, params={"state": state, "per_page": 100})
        response.raise_for_status()
        prs = response.json()
        logger.info("Found %d pull requests (%s).", len(prs), state)
        return prs

    # ------------------------------------------------------------------
    # Webhook helpers
    # ------------------------------------------------------------------

    def create_webhook(
        self,
        owner: str,
        repo: str,
        url: str,
        events: list[str] | None = None,
        secret: str | None = None,
    ) -> dict:
        """
        Register a webhook on a repository.

        Args:
            owner: Repository owner.
            repo: Repository name.
            url: The payload URL that GitHub will POST events to.
            events: List of event types to subscribe to. Defaults to
                    ``["push", "pull_request"]``.
            secret: Optional HMAC secret used to sign webhook payloads.

        Returns:
            Created webhook object.
        """
        if events is None:
            events = ["push", "pull_request"]
        config: dict = {"url": url, "content_type": "json"}
        if secret:
            config["secret"] = secret
        payload = {"name": "web", "active": True, "events": events, "config": config}
        api_url = f"{GITHUB_API_BASE}/repos/{owner}/{repo}/hooks"
        response = self.session.post(api_url, json=payload)
        response.raise_for_status()
        hook = response.json()
        logger.info("Webhook created (id=%s) for %s/%s.", hook["id"], owner, repo)
        return hook

    def run(self, owner: str, repo: str) -> dict:
        """
        Execute the full GitHub workflow for the given repository.

        Fetches the repository details and its open issues and pull requests.

        Args:
            owner: Repository owner.
            repo: Repository name.

        Returns:
            Dictionary with ``repo``, ``issues``, and ``pull_requests`` keys.
        """
        logger.info("Running GitHub workflow for %s/%s …", owner, repo)
        repo_info = self.get_repo(owner, repo)
        issues = self.list_issues(owner, repo)
        prs = self.list_pull_requests(owner, repo)
        result = {"repo": repo_info, "issues": issues, "pull_requests": prs}
        logger.info(
            "GitHub workflow complete: %d issues, %d PRs.", len(issues), len(prs)
        )
        return result
