"""Configuration settings using pydantic-settings."""

import json
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

env_dir = Path(__file__).parent.parent
env_path = env_dir / ".env"
print(f"env_path - {env_path}")


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=env_path, extra="ignore")
    """Application settings."""

    DEBUG: bool = True
    app_port: int = 8080
    app_host: str = "0.0.0.0"
    MTX_WORK_DIR: Path = env_dir / "work"
    MTX_JSON_DIR: Path = env_dir / "work/json"
    MTX_YAML_FILE: Path = env_dir / "work/mediamtx01.yml"
    MTX_YAML_BACKUP_FILE: Path = env_dir / "work/mediamtx01.yml.bak"
    log_level: str = "INFO"


settings = Settings()

if settings.DEBUG:
    if env_path.exists():
        print("Environment variables loaded from %s", env_path)
        print(
            "Application settings initialized: %s",
            json.dumps(settings.model_dump(), indent=2, default=str),
        )
