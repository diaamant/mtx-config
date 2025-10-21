from abc import ABC, abstractmethod
from typing import Dict, Any


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
