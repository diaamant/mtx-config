"""Configuration settings using pydantic-settings."""
from pathlib import Path
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""
    
    app_port: int = 8080
    app_host: str = "0.0.0.0"
    work_dir: Path = Path("work")
    json_dir: Path = Path("work/json")
    yaml_file: Path = Path("work/mediamtx01.yml")
    yaml_backup_file: Path = Path("work/mediamtx01.yml.bak")
    log_level: str = "INFO"
    
    class Config:
        env_file = ".env"
        env_prefix = "MTX_"


settings = Settings()
