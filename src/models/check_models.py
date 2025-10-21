"""Data models and validation schemas using Pydantic."""

import re
from typing import Any, Dict
from typing import Optional

from pydantic import BaseModel, Field, field_validator, ConfigDict


class StreamConfig(BaseModel):
    """Base configuration for a media stream."""

    # model_config is an instance of ConfigDict in V2
    model_config = ConfigDict(
        extra="allow",  # Allow additional fields not explicitly defined
        validate_assignment=True,  # Validate on assignment
    )

    source: Optional[str] = None
    runOnDemand: Optional[str] = None
    runOnDemandRestart: Optional[bool] = None
    runOnReadyRestart: Optional[bool] = None
    runOnDemandStartTimeout: Optional[str] = None
    rtspTransport: Optional[str] = Field(None, pattern=r"^(udp|tcp|auto)$")
    sourceOnDemand: Optional[bool] = None

    # Use @field_validator with mode='after' (default) for validation after type coercion
    @field_validator("runOnDemandStartTimeout")
    @classmethod
    def validate_timeout(cls, v: Optional[str]) -> Optional[str]:
        """Validate timeout format (e.g., '9s', '10m', '1h')."""
        if v is None:
            return v
        # Use a raw string for the regex pattern for clarity
        if not re.match(r"^\d+[smh]$", v):
            raise ValueError(
                "Timeout must be in format: digits + s/m/h (e.g., '9s', '10m', '1h')"
            )
        return v

    @field_validator("source")
    @classmethod
    def validate_source(cls, v: Optional[str]) -> Optional[str]:
        """Validate RTSP/RTMP source URL."""
        if v is None:
            return v
        if not v.startswith(
            ("rtsp://", "rtmp://", "rtsps://", "rtmps://", "http://", "https://")
        ):
            raise ValueError("Source must be a valid RTSP/RTMP/HTTP URL")
        return v


class PathsConfig(BaseModel):
    """Configuration for all paths/streams."""

    model_config = ConfigDict(
        validate_assignment=True,
    )

    paths: Dict[str, StreamConfig] = Field(default_factory=dict)

    def add_stream(self, name: str, config: Dict[str, Any]) -> None:
        """Add a new stream with validation."""
        # Инициализация остается прежней
        self.paths[name] = StreamConfig.model_validate(config)

    def remove_stream(self, name: str) -> None:
        """Remove a stream."""
        if name in self.paths:
            del self.paths[name]

    def get_stream(self, name: str) -> Optional[StreamConfig]:
        """Get a stream configuration."""
        return self.paths.get(name)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        # model_dump() - это метод V2, соответствующий .dict() из V1
        return {
            name: config.model_dump(exclude_none=True)
            for name, config in self.paths.items()
        }


class AuthConfig(BaseModel):
    """Authentication configuration."""

    model_config = ConfigDict(
        extra="allow",
        validate_assignment=True,
    )

    authMethod: Optional[str] = Field(None, pattern="^(internal|jwt|http)$")
    authInternalUsers: Optional[list[Dict[str, str]]] = None
    authHTTPAddress: Optional[str] = None
    authHTTPExclude: Optional[list[str]] = None


class RTSPConfig(BaseModel):
    """RTSP server configuration."""

    model_config = ConfigDict(
        extra="allow",
        validate_assignment=True,
    )

    rtsp: Optional[bool] = True
    rtspAddress: Optional[str] = Field(None, pattern=r"^(:?[\w\-\.]*:\d+)$")
    rtspEncryption: Optional[str] = Field(None, pattern="^(no|optional|strict)$")
