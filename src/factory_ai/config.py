"""Configuration management for Factory.ai connections."""

import json
import os
from pathlib import Path
from typing import Any, Dict, List, Optional


DEFAULT_CONFIG_DIR = Path.home() / ".factory_ai"
DEFAULT_CONFIG_FILE = DEFAULT_CONFIG_DIR / "connections.json"


class ConfigManager:
    """Manages persisted connection configuration (metadata only — no secrets)."""

    def __init__(self, config_path: Optional[Path] = None):
        self.config_path = config_path or DEFAULT_CONFIG_FILE

    def _load(self) -> Dict[str, Any]:
        if not self.config_path.exists():
            return {"connections": {}}
        with open(self.config_path, "r", encoding="utf-8") as fh:
            return json.load(fh)

    def _save(self, data: Dict[str, Any]) -> None:
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.config_path, "w", encoding="utf-8") as fh:
            json.dump(data, fh, indent=2)

    def save_connection(self, connection_data: Dict[str, Any]) -> None:
        """Persist connection metadata (no credentials) under its name."""
        data = self._load()
        name = connection_data["name"]
        data["connections"][name] = connection_data
        self._save(data)

    def get_connection(self, name: str) -> Optional[Dict[str, Any]]:
        """Retrieve connection metadata by name."""
        data = self._load()
        return data["connections"].get(name)

    def list_connections(self) -> List[Dict[str, Any]]:
        """List all saved connection metadata entries."""
        data = self._load()
        return list(data["connections"].values())

    def remove_connection(self, name: str) -> bool:
        """Remove a connection by name. Returns True if it existed."""
        data = self._load()
        if name in data["connections"]:
            del data["connections"][name]
            self._save(data)
            return True
        return False
