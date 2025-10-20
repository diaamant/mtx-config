import json
import warnings
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

# --- Конфигурация путей ---
env_dir = Path(__file__).parent.parent.parent
env_path = env_dir / ".env"
print(f"env_path - {env_path}")


# --- Определение настроек ---
class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=env_path, extra="ignore")
    """Application settings."""

    DEBUG: bool = True
    app_port: int = 8080
    app_host: str = "localhost"
    MTX_WORK_DIR: Path = env_dir / "work"
    MTX_JSON_DIR: Path = env_dir / "work/json"
    MTX_YAML_FILE: Path = env_dir / "work/mediamtx01.yml"
    MTX_YAML_BACKUP_FILE: Path = env_dir / "work/mediamtx01.yml.bak"
    log_level: str = "INFO"


# --- Вспомогательная функция для отладки ---
def _debug_print_settings(settings: Settings) -> None:
    if settings.DEBUG:
        if env_path.exists():
            # Исправлена ошибка форматирования строки
            print(f"Environment variables loaded from {env_path}")
        # Исправлена ошибка форматирования строки
        print(
            f"Application settings initialized: {json.dumps(settings.model_dump(), indent=2, default=str)}"
        )


# --- Реализация Singleton (паттерн "Модуль") ---
# Создаем единственный экземпляр СРАЗУ при импорте модуля.
# Это гарантирует, что он будет создан только один раз.
_settings_instance = Settings()
_debug_print_settings(_settings_instance)  # Выводим отладку при создании


def get_settings() -> Settings:
    return _settings_instance


# --- Обратная совместимость ---
def __getattr__(name: str):
    """
    Обеспечивает обратную совместимость для 'from src.core.config import settings'.

    DEPRECATED: Используйте get_settings() напрямую.
    """
    if name == "settings":
        warnings.warn(
            "Direct import of 'settings' is deprecated. Use 'get_settings()' instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        return get_settings()
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
