"""
AllBots.com integration client for Factory.ai.

Provides :class:`AllBotsClient` for publishing bot events and deploying
bots/swarms to the AllBots platform via its REST API.
"""

from __future__ import annotations

import os
from typing import Any


class AllBotsClient:
    """Thin wrapper around the AllBots.com REST API.

    Parameters
    ----------
    api_key:
        AllBots API key.  Defaults to the ``ALLBOTS_API_KEY`` environment
        variable when not supplied explicitly.
    base_url:
        Base URL of the AllBots API.  Override for staging/test environments.
    """

    DEFAULT_BASE_URL = "https://api.allbots.com/v1"

    def __init__(
        self,
        api_key: str | None = None,
        base_url: str = DEFAULT_BASE_URL,
    ) -> None:
        self.api_key = api_key or os.environ.get("ALLBOTS_API_KEY", "")
        self.base_url = base_url.rstrip("/")

    # ------------------------------------------------------------------
    # Public helpers
    # ------------------------------------------------------------------

    def deploy_bot(self, manifest: dict[str, Any]) -> dict[str, Any]:
        """Deploy a bot described by *manifest* to the AllBots platform.

        Parameters
        ----------
        manifest:
            Parsed ``bot.yaml`` content.

        Returns
        -------
        dict[str, Any]
            API response payload (deployment ID, status, etc.).
        """
        return self._post("/bots/deploy", body=manifest)

    def deploy_swarm(
        self, bots: list[str], coordinator: str = "round-robin"
    ) -> dict[str, Any]:
        """Create a swarm from the given list of bot names.

        Parameters
        ----------
        bots:
            List of already-deployed bot names to include in the swarm.
        coordinator:
            Swarm coordination strategy (e.g. ``"round-robin"``).

        Returns
        -------
        dict[str, Any]
            API response payload (swarm ID, status, etc.).
        """
        body = {"bots": bots, "coordinator": coordinator}
        return self._post("/swarms/create", body=body)

    def publish_event(self, queue: str, event: dict[str, Any]) -> dict[str, Any]:
        """Publish an *event* to the specified AllBots *queue*.

        Parameters
        ----------
        queue:
            Target queue name (as configured in ``bot.yaml``).
        event:
            Arbitrary event payload.

        Returns
        -------
        dict[str, Any]
            API response payload.
        """
        body = {"queue": queue, "event": event}
        return self._post("/events/publish", body=body)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _post(self, path: str, body: dict[str, Any]) -> dict[str, Any]:
        """Send a POST request to the AllBots API.

        This is a thin stub that can be replaced with a real HTTP client
        (e.g. ``httpx`` or ``requests``) when the package is wired up.
        """
        raise NotImplementedError(
            "AllBotsClient._post must be implemented with a real HTTP client. "
            "Install 'httpx' or 'requests' and replace this stub."
        )
