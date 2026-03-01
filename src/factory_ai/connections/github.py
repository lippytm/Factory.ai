"""GitHub connection workflow for Factory.ai."""

import urllib.request
import urllib.error
import json
from typing import Any, Dict, Optional

from .base import BaseConnection


class GitHubConnection(BaseConnection):
    """Connection workflow for GitHub using a personal access token or OAuth token."""

    API_URL = "https://api.github.com"

    def __init__(self, name: str = "github"):
        super().__init__(name)
        self._username: Optional[str] = None

    def connect(self, token: str, **kwargs) -> bool:
        """Connect to GitHub with a personal access token.

        Args:
            token: GitHub personal access token or OAuth token.

        Returns:
            True if authentication succeeded, False otherwise.
        """
        if not token:
            raise ValueError("GitHub token must not be empty.")
        self._credentials = {"token": token}
        return self.validate()

    def validate(self) -> bool:
        """Validate the GitHub token by calling the /user endpoint."""
        token = self._credentials.get("token")
        if not token:
            self._connected = False
            return False
        try:
            req = urllib.request.Request(
                f"{self.API_URL}/user",
                headers={
                    "Authorization": f"Bearer {token}",
                    "Accept": "application/vnd.github+json",
                    "X-GitHub-Api-Version": "2022-11-28",
                },
            )
            with urllib.request.urlopen(req, timeout=10) as resp:
                data = json.loads(resp.read().decode())
                self._username = data.get("login")
                self._connected = True
                return True
        except (urllib.error.HTTPError, urllib.error.URLError, json.JSONDecodeError):
            self._connected = False
            return False

    def to_dict(self) -> Dict[str, Any]:
        result = super().to_dict()
        result["username"] = self._username
        return result
