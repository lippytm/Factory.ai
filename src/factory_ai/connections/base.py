"""Base connection class for Factory.ai."""

import abc
from typing import Any, Dict, Optional


class BaseConnection(abc.ABC):
    """Abstract base class for all connection types."""

    def __init__(self, name: str):
        self.name = name
        self._connected = False
        self._credentials: Dict[str, Any] = {}

    @property
    def is_connected(self) -> bool:
        return self._connected

    @abc.abstractmethod
    def connect(self, **credentials) -> bool:
        """Establish a connection using the provided credentials.

        Returns True if connection succeeded, False otherwise.
        """

    @abc.abstractmethod
    def validate(self) -> bool:
        """Validate that the current connection is active and working."""

    def disconnect(self) -> None:
        """Close the connection and clear credentials."""
        self._connected = False
        self._credentials = {}

    def to_dict(self) -> Dict[str, Any]:
        """Serialize connection metadata (no secrets) to a dictionary."""
        return {
            "name": self.name,
            "type": self.__class__.__name__,
            "connected": self._connected,
        }

    def __repr__(self) -> str:
        status = "connected" if self._connected else "disconnected"
        return f"{self.__class__.__name__}(name={self.name!r}, status={status})"
