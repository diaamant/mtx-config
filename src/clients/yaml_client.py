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

    def import_config(self, yaml_data: Dict[str, Any]) -> Dict[str, Any]:
        """Import configuration from parsed YAML data.

        Args:
            yaml_data: Parsed YAML data (as dict)

        Returns:
            Dict[str, Any]: Configuration in internal format
        """
        try:
            # Convert YAML structure back to internal format
            return self._convert_from_yaml_structure(yaml_data)

        except Exception as e:
            logger.error(f"Failed to import config from YAML: {e}")
            raise

    def _convert_to_yaml_structure(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Convert internal data structure to YAML-compatible format."""
        yaml_data = {}

        # Handle app data first, which goes to the root
        if "values_app.json" in data:
            yaml_data.update(data["values_app.json"])

        # Map other internal file names to YAML sections
        section_mapping = {
            "auth.json": "auth",
            "values_rtsp.json": "rtsp",
            "values_webrtc.json": "webrtc",
            "values_hls.json": "hls",
            "values_rtmp.json": "rtmp",
            "values_srt.json": "srt",
            "values_pathDefaults.json": "pathDefaults",
            "paths.json": "paths",
        }

        # Convert each section
        for file_name, section in section_mapping.items():
            if file_name in data:
                yaml_data[section] = data[file_name]

        return yaml_data

    def _convert_from_yaml_structure(self, yaml_data: Dict[str, Any]) -> Dict[str, Any]:
        """Convert YAML structure back to internal format."""
        internal_data = {}
        app_data = {}

        # Map YAML sections back to internal file names
        section_mapping = {
            "auth": "auth.json",
            "rtsp": "values_rtsp.json",
            "webrtc": "values_webrtc.json",
            "hls": "values_hls.json",
            "rtmp": "values_rtmp.json",
            "srt": "values_srt.json",
            "pathDefaults": "values_pathDefaults.json",
            "paths": "paths.json",
        }

        # Separate root-level keys from sections
        for key, value in yaml_data.items():
            if key in section_mapping:
                internal_data[section_mapping[key]] = value
            else:
                app_data[key] = value

        if app_data:
            internal_data["values_app.json"] = app_data

        return internal_data

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
