import shutil
from pathlib import Path
from typing import Dict, Any

import yaml

from src.clients.abc_conf_client import ConfigClient
from src.clients.json_client import JSONClient
from src.core.config import get_settings as get_settings_func
from src.core.log import logger


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
