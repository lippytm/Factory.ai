"""AllBots.com connection workflow for Factory.ai."""

import urllib.request
import urllib.error
import json
from typing import Any, Dict, Optional

from .base import BaseConnection


class AllBotsConnection(BaseConnection):
    """Connection workflow for AllBots.com using an API key."""

    API_URL = "https://allbots.com/api/v1"

    def __init__(self, name: str = "allbots", api_url: Optional[str] = None):
        super().__init__(name)
        if api_url:
            self.API_URL = api_url
        self._bot_name: Optional[str] = None

    def connect(self, api_key: str, **kwargs) -> bool:
        """Connect to AllBots.com with an API key.

        Args:
            api_key: AllBots.com API key.

        Returns:
            True if authentication succeeded, False otherwise.
        """
        if not api_key:
            raise ValueError("AllBots API key must not be empty.")
        self._credentials = {"api_key": api_key}
        return self.validate()

    def validate(self) -> bool:
        """Validate the AllBots.com API key by calling the /me endpoint."""
        api_key = self._credentials.get("api_key")
        if not api_key:
            self._connected = False
            return False
        try:
            req = urllib.request.Request(
                f"{self.API_URL}/me",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                },
            )
            with urllib.request.urlopen(req, timeout=10) as resp:
                data = json.loads(resp.read().decode())
                self._bot_name = data.get("bot_name") or data.get("name")
                self._connected = True
                return True
        except (urllib.error.HTTPError, urllib.error.URLError, json.JSONDecodeError):
            self._connected = False
            return False

    def to_dict(self) -> Dict[str, Any]:
        result = super().to_dict()
        result["bot_name"] = self._bot_name
        return result
