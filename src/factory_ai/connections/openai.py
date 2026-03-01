"""OpenAI/ChatGPT connection workflow for Factory.ai."""

import urllib.request
import urllib.error
import json
from typing import Any, Dict, Optional

from .base import BaseConnection


class OpenAIConnection(BaseConnection):
    """Connection workflow for OpenAI (ChatGPT) using an API key."""

    API_URL = "https://api.openai.com/v1"

    def __init__(self, name: str = "openai"):
        super().__init__(name)
        self._organization: Optional[str] = None

    def connect(self, api_key: str, organization: Optional[str] = None, **kwargs) -> bool:
        """Connect to OpenAI with an API key.

        Args:
            api_key: OpenAI API key (starts with 'sk-').
            organization: Optional OpenAI organization ID.

        Returns:
            True if authentication succeeded, False otherwise.
        """
        if not api_key:
            raise ValueError("OpenAI API key must not be empty.")
        self._credentials = {"api_key": api_key}
        if organization:
            self._credentials["organization"] = organization
            self._organization = organization
        return self.validate()

    def validate(self) -> bool:
        """Validate the OpenAI API key by listing available models."""
        api_key = self._credentials.get("api_key")
        if not api_key:
            self._connected = False
            return False
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }
        organization = self._credentials.get("organization")
        if organization:
            headers["OpenAI-Organization"] = organization
        try:
            req = urllib.request.Request(
                f"{self.API_URL}/models",
                headers=headers,
            )
            with urllib.request.urlopen(req, timeout=10) as resp:
                json.loads(resp.read().decode())
                self._connected = True
                return True
        except (urllib.error.HTTPError, urllib.error.URLError, json.JSONDecodeError):
            self._connected = False
            return False

    def to_dict(self) -> Dict[str, Any]:
        result = super().to_dict()
        result["organization"] = self._organization
        return result
