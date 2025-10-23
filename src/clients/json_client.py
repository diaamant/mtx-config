import json
from pathlib import Path
from typing import Dict, Any

from src.clients.abc_conf_client import ConfigClient
from src.core.config import get_settings as get_settings_func
from src.core.log import logger


# --- реализация для JSON ---
class JSONClient(ConfigClient):
    """
    Клиент для работы с набором JSON-файлов в директории.
    Отвечает за чтение и запись отдельных JSON-файлов.
    """

    def __init__(self):
        self.json_dir: Path = get_settings_func().MTX_JSON_DIR

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
                data[json_file.stem] = content
                data[f"{json_file.stem}_enabled"] = True
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
