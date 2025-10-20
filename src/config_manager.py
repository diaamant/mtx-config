"""ConfigManager class for centralized data management."""

import json
import logging
from pathlib import Path
from typing import Any, Callable, Dict, Optional

from pydantic import ValidationError

from src.core.config import settings
from src.models.test_models import AuthConfig, PathsConfig, RTSPConfig, StreamConfig

logger = logging.getLogger(__name__)


class ConfigManager:
    """Centralized configuration manager with validation and observers."""

    def __init__(self, json_dir: Optional[Path] = None):
        """Initialize ConfigManager."""
        self.json_dir = json_dir or settings.json_dir
        self.data: Dict[str, Any] = {}
        self.observers: list[Callable] = []
        self._paths_config: Optional[PathsConfig] = None

    def load_data(self) -> Dict[str, Any]:
        """Load all JSON files into the data dictionary."""
        self.data = {}

        if not self.json_dir.exists():
            logger.warning(f"JSON directory does not exist: {self.json_dir}")
            return self.data

        for json_file in self.json_dir.glob("*.json"):
            # Skip _enabled files
            if json_file.name.endswith("_enabled"):
                continue

            try:
                with open(json_file, "r", encoding="utf-8") as f:
                    content = json.load(f)
                    self.data[json_file.name] = content
                    self.data[f"{json_file.name}_enabled"] = True
                    logger.debug(f"Loaded {json_file.name}")
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse {json_file.name}: {e}")
            except Exception as e:
                logger.error(f"Error loading {json_file.name}: {e}")

        # Initialize PathsConfig with validation
        if "paths.json" in self.data:
            try:
                self._paths_config = PathsConfig(
                    paths={
                        name: StreamConfig(**config)
                        for name, config in self.data["paths.json"].items()
                    }
                )
            except ValidationError as e:
                logger.error(f"Validation error in paths.json: {e}")
                # Keep original data but log validation errors

        return self.data

    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value."""
        return self.data.get(key, default)

    def set(self, key: str, value: Any, validate: bool = True) -> bool:
        """Set configuration value with optional validation."""
        try:
            if validate:
                # Validate specific configurations
                if key == "paths.json" and isinstance(value, dict):
                    # Validate each stream
                    for stream_name, stream_config in value.items():
                        StreamConfig(**stream_config)
                elif key == "auth.json" and isinstance(value, dict):
                    AuthConfig(**value)
                elif key == "values_rtsp.json" and isinstance(value, dict):
                    RTSPConfig(**value)

            self.data[key] = value
            self._notify_observers(key, value)
            logger.debug(f"Set {key}")
            return True

        except ValidationError as e:
            logger.error(f"Validation error setting {key}: {e}")
            return False
        except Exception as e:
            logger.error(f"Error setting {key}: {e}")
            return False

    def add_stream(self, name: str, stream_type: str) -> bool:
        """Add a new stream with validation."""
        try:
            if "paths.json" not in self.data:
                self.data["paths.json"] = {}

            if name in self.data["paths.json"]:
                logger.warning(f"Stream {name} already exists")
                return False

            # Create stream based on type
            if stream_type == "Source":
                config = {
                    "source": "rtsp://",
                    "rtspTransport": "udp",
                    "sourceOnDemand": False,
                }
            elif stream_type == "RunOnDemand":
                config = {
                    "runOnDemand": "ffmpeg",
                    "runOnDemandRestart": False,
                    "runOnDemandStartTimeout": "10s",
                }
            else:
                logger.error(f"Invalid stream type: {stream_type}")
                return False

            # Validate
            StreamConfig(**config)

            # Add to data
            self.data["paths.json"][name] = config

            # Update paths config
            if self._paths_config:
                self._paths_config.add_stream(name, config)

            self._notify_observers("paths.json", self.data["paths.json"])
            logger.info(f"Added stream: {name} (type: {stream_type})")
            return True

        except ValidationError as e:
            logger.error(f"Validation error adding stream {name}: {e}")
            return False
        except Exception as e:
            logger.error(f"Error adding stream {name}: {e}")
            return False

    def remove_stream(self, name: str) -> bool:
        """Remove a stream."""
        try:
            if "paths.json" not in self.data or name not in self.data["paths.json"]:
                logger.warning(f"Stream {name} not found")
                return False

            del self.data["paths.json"][name]

            # Update paths config
            if self._paths_config:
                self._paths_config.remove_stream(name)

            self._notify_observers("paths.json", self.data["paths.json"])
            logger.info(f"Removed stream: {name}")
            return True

        except Exception as e:
            logger.error(f"Error removing stream {name}: {e}")
            return False

    def update_stream(self, name: str, config: Dict[str, Any]) -> bool:
        """Update stream configuration with validation."""
        try:
            if "paths.json" not in self.data or name not in self.data["paths.json"]:
                logger.warning(f"Stream {name} not found")
                return False

            # Validate
            StreamConfig(**config)

            # Update
            self.data["paths.json"][name] = config

            # Update paths config
            if self._paths_config:
                self._paths_config.paths[name] = StreamConfig(**config)

            self._notify_observers("paths.json", self.data["paths.json"])
            logger.debug(f"Updated stream: {name}")
            return True

        except ValidationError as e:
            logger.error(f"Validation error updating stream {name}: {e}")
            return False
        except Exception as e:
            logger.error(f"Error updating stream {name}: {e}")
            return False

    def register_observer(self, callback: Callable[[str, Any], None]) -> None:
        """Register an observer for data changes."""
        if callback not in self.observers:
            self.observers.append(callback)
            logger.debug(f"Registered observer: {callback.__name__}")

    def unregister_observer(self, callback: Callable[[str, Any], None]) -> None:
        """Unregister an observer."""
        if callback in self.observers:
            self.observers.remove(callback)
            logger.debug(f"Unregistered observer: {callback.__name__}")

    def _notify_observers(self, key: str, value: Any) -> None:
        """Notify all observers of data change."""
        for observer in self.observers:
            try:
                observer(key, value)
            except Exception as e:
                logger.error(f"Error notifying observer {observer.__name__}: {e}")

    def validate_all(self) -> Dict[str, list[str]]:
        """Validate all configurations and return errors."""
        errors: Dict[str, list[str]] = {}

        # Validate paths
        if "paths.json" in self.data:
            for stream_name, stream_config in self.data["paths.json"].items():
                try:
                    StreamConfig(**stream_config)
                except ValidationError as e:
                    errors[f"paths.json:{stream_name}"] = [
                        str(err) for err in e.errors()
                    ]

        # Validate auth
        if "auth.json" in self.data:
            try:
                AuthConfig(**self.data["auth.json"])
            except ValidationError as e:
                errors["auth.json"] = [str(err) for err in e.errors()]

        # Validate RTSP
        if "values_rtsp.json" in self.data:
            try:
                RTSPConfig(**self.data["values_rtsp.json"])
            except ValidationError as e:
                errors["values_rtsp.json"] = [str(err) for err in e.errors()]

        return errors
