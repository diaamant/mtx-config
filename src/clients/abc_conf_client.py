from abc import ABC, abstractmethod
from typing import Dict, Any, Optional


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

    def export_config(self, data: Dict[str, Any]) -> str:
        """Экспортирует конфигурацию в строку (например, YAML).

        Args:
            data: Конфигурационные данные во внутреннем формате

        Returns:
            str: Строковое представление конфигурации
        """
        raise NotImplementedError("Export not implemented for this client")

    def import_config(self, config_data: Dict[str, Any]) -> Dict[str, Any]:
        """Импортирует конфигурацию из внешнего формата.

        Args:
            config_data: Данные конфигурации во внешнем формате

        Returns:
            Dict[str, Any]: Конфигурация во внутреннем формате
        """
        raise NotImplementedError("Import not implemented for this client")
