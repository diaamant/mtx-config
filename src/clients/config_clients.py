from functools import lru_cache

from src.clients.abc_conf_client import ConfigClient
from src.clients.json_client import JSONClient
from src.clients.yaml_client import YAMLClient
from src.core.log import logger


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
