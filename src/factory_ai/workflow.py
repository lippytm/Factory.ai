"""Connection workflow orchestrator for Factory.ai."""

from pathlib import Path
from typing import Any, Dict, List, Optional, Type

from .connections.base import BaseConnection
from .connections.github import GitHubConnection
from .connections.openai import OpenAIConnection
from .connections.allbots import AllBotsConnection
from .config import ConfigManager


_CONNECTION_TYPES: Dict[str, Type[BaseConnection]] = {
    "github": GitHubConnection,
    "openai": OpenAIConnection,
    "chatgpt": OpenAIConnection,
    "allbots": AllBotsConnection,
}


class ConnectionWorkflow:
    """High-level workflow for creating and managing service connections.

    Supported service types: github, openai (chatgpt), allbots.

    Example::

        wf = ConnectionWorkflow()

        # Create a GitHub connection
        conn = wf.create("github", token="ghp_...")

        # Create an OpenAI connection
        conn = wf.create("openai", api_key="sk-...")

        # List saved connections
        connections = wf.list_connections()
    """

    def __init__(self, config_path: Optional[Path] = None):
        self._config = ConfigManager(config_path)
        self._active: Dict[str, BaseConnection] = {}

    # ------------------------------------------------------------------
    # Public workflow methods
    # ------------------------------------------------------------------

    def create(self, service: str, name: Optional[str] = None, **credentials) -> BaseConnection:
        """Create and validate a new connection to *service*.

        Args:
            service: One of ``github``, ``openai`` / ``chatgpt``, ``allbots``.
            name: Optional friendly name for the connection. Defaults to *service*.
            **credentials: Service-specific credentials (see connection classes).

        Returns:
            A :class:`~factory_ai.connections.base.BaseConnection` instance.

        Raises:
            ValueError: If *service* is not recognised or credentials are invalid.
            ConnectionError: If the connection validation fails.
        """
        service_key = service.lower()
        if service_key not in _CONNECTION_TYPES:
            raise ValueError(
                f"Unknown service {service!r}. "
                f"Supported: {sorted(_CONNECTION_TYPES.keys())}"
            )

        conn_name = name or service_key
        cls = _CONNECTION_TYPES[service_key]
        conn = cls(name=conn_name)
        success = conn.connect(**credentials)
        if not success:
            raise ConnectionError(
                f"Failed to connect to {service!r}. "
                "Please check your credentials and try again."
            )

        self._active[conn_name] = conn
        self._config.save_connection(conn.to_dict())
        return conn

    def get(self, name: str) -> Optional[BaseConnection]:
        """Return an active in-memory connection by name, or None."""
        return self._active.get(name)

    def list_connections(self) -> List[Dict[str, Any]]:
        """List all saved connection metadata from the config store."""
        return self._config.list_connections()

    def remove(self, name: str) -> bool:
        """Remove a connection from the config store and active cache.

        Returns True if the connection existed and was removed.
        """
        self._active.pop(name, None)
        return self._config.remove_connection(name)

    @staticmethod
    def supported_services() -> List[str]:
        """Return the list of supported service identifiers."""
        return sorted(set(_CONNECTION_TYPES.keys()))
