import shutil
from pathlib import Path
from typing import Dict, Any

import yaml
from requests.packages import imported_mod

from src.clients.abc_conf_client import ConfigClient
from src.clients.json_client import JSONClient
from src.core.config import get_settings as get_settings_func
from src.core.keys import TAB_KEYS, NAMES_TAB, TAB_NAMES
from src.core.log import logger


def _pop_keys_to_dict(source_dict: Dict[str, Any], keys_list: list) -> Dict[str, Any]:
    """
    Извлекает (с удалением) ключи из source_dict в новый словарь.
    """
    return {key: source_dict.pop(key) for key in keys_list if key in source_dict}


# --- реализация для YAML ---
class YAMLClient(ConfigClient):
    """
    Клиент для работы с финальным YAML-файлом.
    Отвечает за сборку и сохранение mediamtx.yml.
    """

    def __init__(self):
        settings = get_settings_func()
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

    def _convert_to_yaml_structure(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Convert internal data structure to YAML-compatible format."""
        final_config = {}
        for key_section, content in data.items():
            if "_enabled" in key_section or not content:
                continue

            if key_section == "paths":
                final_config["paths"] = content
            elif key_section == "pathDefaults":
                final_config["pathDefaults"] = content
            else:
                # All other keys go to the root
                final_config.update(content)

        return final_config

    def export_config(self, data: Dict[str, Any]) -> str:
        """Export configuration as YAML string.

        Args:
            data: Configuration data in internal format

        Returns:
            str: YAML-formatted configuration string
        """
        try:
            # Convert internal format to YAML-compatible structure
            yaml_data = self._convert_to_yaml_structure(data)

            # Convert to YAML string with nice formatting
            yaml_content = yaml.dump(
                yaml_data,
                default_flow_style=False,
                sort_keys=False,
                allow_unicode=True,
                encoding="utf-8",
                width=120,
            )

            if isinstance(yaml_content, bytes):
                yaml_content = yaml_content.decode("utf-8")

            return yaml_content

        except Exception as e:
            logger.error(f"Failed to export config to YAML: {e}")
            raise

    def _convert_from_yaml_structure(self, yaml_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Разделяет основной словарь конфигурации на части согласно TAB_KEYS.
        """
        imported_data = {}
        # Make a copy to avoid modifying the original dict while iterating
        config_data = yaml_data.copy()

        for tab_key, keys_or_name in TAB_KEYS.items():
            key_section = f"{NAMES_TAB[tab_key]}"
            if isinstance(keys_or_name, list):
                # Pop a group of keys
                imported_data[key_section] = _pop_keys_to_dict(config_data, keys_or_name)
            elif isinstance(keys_or_name, str):
                # Pop a single section (like pathDefaults or paths)
                imported_data[key_section] = config_data.pop(keys_or_name, None)
            imported_data[f"{key_section}_enabled"] = True

        # Whatever is left in config_data is app_data
        imported_data[f"{NAMES_TAB['APP']}"] = config_data
        return imported_data

    def import_config(self, yaml_data: Dict[str, Any]) -> Dict[str, Any]:
        """Import configuration from parsed YAML data.

        Args:
            yaml_data: Parsed YAML data (as dict)

        Returns:
            Dict[str, Any]: Configuration in internal format
        """
        try:
            return self._convert_from_yaml_structure(yaml_data)

        except Exception as e:
            logger.error(f"Failed to import config from YAML: {e}")
            raise

    def save_config(self, data: Dict[str, Any]) -> None:
        """
        Собирает данные из словаря в единый YAML-файл.
        Эта функция — ваша бывшая `save_data()` из yaml_utils.
        """
        logger.debug(f"YAMLClient: Saving final config to {self.yaml_file}")

        # Шаг 1: Сохраняем JSON-файлы (делегируем JSONClient)
        # self.json_client.save_config(data)

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
        for key_section, content in data.items():
            if key_section not in TAB_NAMES.keys():
                continue

            if not data.get(f"{key_section}_enabled") or not content:
                continue

            if key_section == "paths":
                final_config["paths"] = content
            elif key_section == "pathDefaults":
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
