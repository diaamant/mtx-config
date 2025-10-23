"""ConfigManager class for centralized data management."""

import json
from pathlib import Path
from typing import Any, Callable, Dict, Optional

import yaml
from pydantic import ValidationError

from src.clients.config_clients import get_config_client
from src.core.config import get_settings
from src.core.log import logger
from src.models.check_models import AuthConfig, PathsConfig, RTSPConfig, StreamConfig


class MtxConfigManager:
    """Centralized configuration manager with validation and observers."""

    def __init__(self, json_dir: Optional[Path] = None):
        """Initialize ConfigManager."""
        settings = get_settings()
        self.json_dir = json_dir or settings.MTX_JSON_DIR
        self.data: Dict[str, Any] = {}
        self.preview_content: Dict[str, Any] = {"yaml": ""}
        self.observers: list[Callable] = []
        self._paths_config: Optional[PathsConfig] = None

    def load_data(self) -> Dict[str, Any]:
        """Load all JSON files into the data dictionary using JSONClient."""
        # Use JSONClient from config_clients.py
        json_client = get_config_client("JSON")
        self.data = json_client.load_config()

        # Initialize PathsConfig with validation
        if "paths" in self.data:
            try:
                self._paths_config = PathsConfig(
                    paths={
                        name: StreamConfig(**config)
                        for name, config in self.data["paths"].items()
                    }
                )
            except ValidationError as e:
                logger.error(f"Validation error in paths.json: {e}")
                # Keep original data but log validation errors

        return self.data

    def export_config(self) -> str:
        """Export current configuration as YAML string.

        Returns:
            str: YAML-formatted configuration string
        """
        try:
            # Get the YAML client
            yaml_client = get_config_client("YAML")

            # Export the configuration to YAML format
            yaml_content = yaml_client.export_config(self.data)

            # Validate the exported YAML
            try:
                # Try to parse back to ensure it's valid YAML
                yaml.safe_load(yaml_content)
                return yaml_content
            except yaml.YAMLError as e:
                logger.error(f"Invalid YAML generated during export: {e}")
                raise ValueError("Failed to generate valid YAML configuration") from e

        except Exception as e:
            logger.error(f"Export failed: {e}", exc_info=True)
            raise

    def import_config(self, yaml_content: str) -> None:
        """Import configuration from YAML string.

        Args:
            yaml_content: YAML-formatted configuration string

        Raises:
            ValueError: If the YAML is invalid or validation fails
        """
        try:
            # Parse YAML content
            try:
                parsed_config = yaml.safe_load(yaml_content)
                if not isinstance(parsed_config, dict):
                    raise ValueError("Invalid YAML format: expected a dictionary")
            except yaml.YAMLError as e:
                raise ValueError(f"Invalid YAML: {e}") from e

            # Get YAML client for validation and conversion
            yaml_client = get_config_client("YAML")

            # Convert YAML to internal format (reverse of export)
            # This is a simplified example - adjust based on your actual data structure
            imported_data = yaml_client.import_config(parsed_config)

            # Validate the imported data
            self._validate_imported_data(imported_data)

            # Update internal state
            self.data = imported_data

            # Update paths config if paths were imported
            if "paths.json" in self.data:
                try:
                    self._paths_config = PathsConfig(
                        paths={
                            name: StreamConfig(**config)
                            for name, config in self.data["paths.json"].items()
                        }
                    )
                except ValidationError as e:
                    logger.error(f"Validation error in imported paths: {e}")
                    raise ValueError(f"Invalid paths configuration: {e}") from e

            # Notify observers about the update
            # Using None for key and value since we're updating multiple values
            self._notify_observers("__all__", None)

            logger.info("Configuration imported successfully")

        except Exception as e:
            logger.error(f"Import failed: {e}", exc_info=True)
            raise

    def _validate_imported_data(self, data: Dict[str, Any]) -> None:
        """Validate imported configuration data.

        Args:
            data: Imported configuration data

        Raises:
            ValueError: If validation fails
        """
        # Add any additional validation logic here
        if not isinstance(data, dict):
            raise ValueError("Configuration must be a dictionary")

        # Example: Ensure required sections exist
        required_sections = ["paths.json"]
        for section in required_sections:
            if section not in data:
                raise ValueError(f"Missing required section: {section}")

    def save_data(self) -> None:
        """Save all data using YAMLClient."""
        yaml_client = get_config_client("YAML")
        yaml_client.save_config(self.data)
        logger.info("Configuration saved successfully via YAMLClient")

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

    def update_preview(self) -> None:
        """Update preview with current configuration."""
        try:
            # Assemble configuration like save does
            final_config = {}
            for json_name, content in self.data.items():
                if json_name.endswith("_enabled"):
                    continue
                if not self.data.get(f"{json_name}_enabled", True):
                    continue
                key = json_name.replace(".json", "")
                final_config[key] = content

            if "paths" not in final_config:
                final_config["paths"] = {}

            self.preview_content["yaml"] = yaml.dump(
                final_config,
                default_flow_style=False,
                sort_keys=False,
                allow_unicode=True,
            )
        except Exception as e:
            logger.error(f"Preview update failed: {e}")
            self.preview_content["yaml"] = f"Error generating preview: {e}"
