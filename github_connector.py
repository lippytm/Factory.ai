"""GitHub repository connector for Factory.ai.

Connects to all repositories for an authenticated GitHub user,
including the newest ones, using the GitHub REST API with pagination.
"""

import os
import requests


class GitHubConnector:
    """Connects to all GitHub repositories for an authenticated user."""

    BASE_URL = "https://api.github.com"

    def __init__(self, token: str | None = None):
        """Initialize with a GitHub personal access token.

        Args:
            token: GitHub personal access token. Falls back to the
                   GITHUB_TOKEN environment variable if not provided.
        """
        self.token = token or os.environ.get("GITHUB_TOKEN")
        if not self.token:
            raise ValueError(
                "A GitHub token is required. Pass token= or set GITHUB_TOKEN."
            )
        self.session = requests.Session()
        self.session.headers.update(
            {
                "Authorization": f"Bearer {self.token}",
                "Accept": "application/vnd.github+json",
                "X-GitHub-Api-Version": "2022-11-28",
            }
        )

    def get_all_repositories(self, sort: str = "created", direction: str = "desc") -> list[dict]:
        """Fetch all repositories the authenticated user has access to.

        Paginates through the GitHub API so that every repository —
        including the most recently created ones — is returned.

        Args:
            sort: Field to sort by. One of ``created``, ``updated``,
                  ``pushed``, or ``full_name``. Defaults to ``created``
                  so the newest repositories appear first.
            direction: Sort direction, ``asc`` or ``desc``.

        Returns:
            A list of repository objects (dicts) as returned by the
            GitHub API.
        """
        repos: list[dict] = []
        url = f"{self.BASE_URL}/user/repos"
        params = {
            "affiliation": "owner,collaborator,organization_member",
            "sort": sort,
            "direction": direction,
            "per_page": 100,
            "page": 1,
        }

        while url:
            response = self.session.get(url, params=params)
            response.raise_for_status()
            page_repos = response.json()
            if not page_repos:
                break
            repos.extend(page_repos)
            # Follow the Link header for the next page, if present.
            url = self._next_page_url(response)
            params = {}  # params are embedded in the next-page URL

        return repos

    def connect(self) -> list[dict]:
        """Connect to all repositories and return their details.

        Returns:
            A list of repository detail dicts, each containing at least
            ``full_name``, ``html_url``, and ``created_at``.
        """
        repos = self.get_all_repositories()
        connected = []
        for repo in repos:
            connected.append(
                {
                    "full_name": repo.get("full_name"),
                    "html_url": repo.get("html_url"),
                    "private": repo.get("private"),
                    "created_at": repo.get("created_at"),
                    "updated_at": repo.get("updated_at"),
                    "default_branch": repo.get("default_branch"),
                }
            )
        return connected

    @staticmethod
    def _next_page_url(response: requests.Response) -> str | None:
        """Extract the 'next' URL from a GitHub Link header, if present."""
        link_header = response.headers.get("Link", "")
        for part in link_header.split(","):
            part = part.strip()
            if 'rel="next"' in part:
                url_part = part.split(";")[0].strip()
                return url_part.strip("<>")
        return None


def main() -> None:
    """Print all connected repositories to stdout."""
    connector = GitHubConnector()
    repos = connector.connect()
    print(f"Connected to {len(repos)} repositories:")
    for repo in repos:
        visibility = "private" if repo["private"] else "public"
        print(f"  {repo['full_name']} ({visibility}) — created {repo['created_at']}")


if __name__ == "__main__":
    main()
