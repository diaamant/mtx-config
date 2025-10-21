from abc import ABC, abstractmethod
from functools import lru_cache
from typing import Dict, Any

from src.clients.json_client import JSONClient
from src.clients.yaml_client import YAMLClient
from src.core.log import logger


class ConfigClient(ABC):
    """
    Абстрактный базовый класс для клиентов конфигурации.
    Определяет контракт, которому должны следовать все клиенты.
    """

    @abstractmethod
    def load_config(self) -> Dict[str, Any]:
        """Загружает конфигурацию из источника и возвращает как словарь."""
        pass

    @abstractmethod
    def save_config(self, data: Dict[str, Any]) -> None:
        """Сохраняет словарь с данными в источник конфигурации."""
        pass


# --- Фабричная функция (Provider) ---

# Словарь для регистрации провайдеров. Легко расширять.
_providers = {
    "JSON": JSONClient,
    "YAML": YAMLClient,
}


@lru_cache()
def get_config_client(provider_name: str) -> ConfigClient:
    """
    Фабричная функция для получения экземпляра клиента конфигурации.
    Использует кэширование для возврата одного и того же экземпляра.
    """
    provider_class = _providers.get(provider_name)
    if not provider_class:
        raise ValueError(f"Unsupported provider: {provider_name}")

    logger.debug(f"Providing instance of {provider_class.__name__}")
    return provider_class()
