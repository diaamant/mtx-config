import json
import shutil
from abc import ABC, abstractmethod
from functools import lru_cache
from pathlib import Path
from typing import Dict, Any

import yaml

from src.core.config import get_settings
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


# --- Конкретная реализация для JSON ---


class JSONClient(ConfigClient):
    """
    Клиент для работы с набором JSON-файлов в директории.
    Отвечает за чтение и запись отдельных JSON-файлов.
    """

    def __init__(self):
        self.json_dir: Path = get_settings().MTX_JSON_DIR

    def load_config(self) -> Dict[str, Any]:
        """
        Загружает все JSON-файлы из директории в один словарь.
        Эта функция — ваша бывшая `load_data()` из json_utils.
        """
        logger.debug(f"JSONClient: Loading data from {self.json_dir}")
        data = {}
        if not self.json_dir.exists():
            logger.error(f"JSON directory not found: {self.json_dir}")
            return data

        for json_file in self.json_dir.glob("*.json"):
            try:
                with open(json_file, "r", encoding="utf-8") as f:
                    content = json.load(f)
                    if not content:
                        logger.warning(f"File {json_file.name} is empty, skipping.")
                        continue
                data[json_file.name] = content
                # Мы можем не добавлять _enabled флаг здесь, т.к. это логика приложения,
                # а не самого процесса загрузки. Но оставим для совместимости.
                data[f"{json_file.name}_enabled"] = True
            except json.JSONDecodeError:
                logger.error(f"Error decoding JSON from {json_file}", exc_info=True)
            except IOError:
                logger.error(f"Error reading file {json_file}", exc_info=True)

        logger.info("JSONClient: Configuration data loaded successfully.")
        return data

    def save_config(self, data: Dict[str, Any]) -> None:
        """
        Сохраняет данные из словаря в отдельные JSON-файлы.
        """
        logger.debug(f"JSONClient: Saving data to {self.json_dir}")
        for key, content in data.items():
            # Сохраняем только те ключи, которые соответствуют именам файлов
            if key.endswith(".json"):
                file_path = self.json_dir / key
                try:
                    if not content:
                        logger.info(f"Skipping write for empty content: {key}")
                        continue
                    with open(file_path, "w", encoding="utf-8") as f:
                        json.dump(content, f, indent=2, ensure_ascii=False)
                except IOError:
                    logger.error(f"Error writing to {file_path}", exc_info=True)
                    # Можно пробросить исключение дальше, если это критично
                    # raise


# --- Конкретная реализация для YAML ---


class YAMLClient(ConfigClient):
    """
    Клиент для работы с финальным YAML-файлом.
    Отвечает за сборку и сохранение mediamtx.yml.
    """

    def __init__(self):
        settings = get_settings()
        self.yaml_file: Path = settings.MTX_YAML_FILE
        self.yaml_backup_file: Path = settings.MTX_YAML_BACKUP_FILE
        # Этот клиент также должен уметь работать с JSON-источниками
        self.json_client = JSONClient()

    def load_config(self) -> Dict[str, Any]:
        """
        Чтение основного YAML-файла не реализовано, так как
        приложение работает с "сырыми" JSON-данными.
        """
        logger.warning("YAMLClient.get_config is not implemented.")
        raise NotImplementedError(
            "This application's workflow is based on reading source JSON files, not the final YAML."
        )

    def save_config(self, data: Dict[str, Any]) -> None:
        """
        Собирает данные из словаря в единый YAML-файл.
        Эта функция — ваша бывшая `save_data()` из yaml_utils.
        """
        logger.debug(f"YAMLClient: Saving final config to {self.yaml_file}")

        # Шаг 1: Сохраняем JSON-файлы (делегируем JSONClient)
        self.json_client.save_config(data)

        # Шаг 2: Создаем бэкап
        if self.yaml_file.exists():
            try:
                shutil.copy(self.yaml_file, self.yaml_backup_file)
                logger.info(f"Backup created: {self.yaml_backup_file}")
            except IOError:
                logger.error("Failed to create configuration backup.", exc_info=True)
                raise

        # Шаг 3: Собираем финальную конфигурацию из словаря `data`
        final_config = {}
        for key, content in data.items():
            if not key.endswith(".json") or not data.get(f"{key}_enabled", True):
                continue

            if not content:
                continue

            # Логика сборки, как у вас и была
            if key == "paths.json":
                final_config["paths"] = content
            elif key == "values_pathDefaults.json":
                final_config["pathDefaults"] = content
            else:
                final_config.update(content)

        # Шаг 4: Записываем финальный YAML
        try:
            with open(self.yaml_file, "w", encoding="utf-8") as f:
                yaml.dump(
                    final_config,
                    f,
                    default_flow_style=False,
                    sort_keys=False,
                    allow_unicode=True,
                )
            logger.info(f"Configuration successfully saved to {self.yaml_file}")
        except (IOError, yaml.YAMLError) as e:
            logger.error(f"Failed to write final YAML file: {e}", exc_info=True)
            raise


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
