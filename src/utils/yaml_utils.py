import json
import shutil

import yaml

from core.config import settings
from src.utils.json_utils import logger


JSON_DIR = settings.MTX_JSON_DIR
YAML_FILE = settings.MTX_YAML_FILE
YAML_BACKUP_FILE = settings.MTX_YAML_BACKUP_FILE


def save_data(data):
    """Save all data back to JSON files and generate the YAML with error handling."""
    try:
        # Save data to JSON files
        for json_file_name, content in data.items():
            if not json_file_name.endswith("_enabled"):
                try:
                    # Пропускаем запись, если контент пустой (None или пустой dict)
                    if not content:
                        logger.info(
                            f"Skipping write for empty content: {json_file_name}"
                        )
                        continue

                    with open(JSON_DIR / json_file_name, "w", encoding="utf-8") as f:
                        json.dump(content, f, indent=2)
                except IOError:
                    logger.error(f"Error writing to {json_file_name}", exc_info=True)
                    raise  # Re-raise to notify the caller

        # Create backup
        if YAML_FILE.exists():
            try:
                shutil.copy(YAML_FILE, YAML_BACKUP_FILE)
                logger.info(f"Backup created: {YAML_BACKUP_FILE}")
            except IOError:
                logger.error("Failed to create configuration backup.", exc_info=True)
                raise

        # --- ИСПРАВЛЕНИЕ 2: Корректная сборка YAML ---
        final_config = {}
        for json_file in sorted(JSON_DIR.glob("*.json")):
            if not data.get(f"{json_file.name}_enabled", True):
                logger.info(f"Skipping disabled section: {json_file.name}")
                continue

            content = data.get(json_file.name)
            if not content:  # Пропускаем пустые секции
                continue

            # 'paths' and 'pathDefaults' - это вложенные словари
            if json_file.name == "paths.json":
                final_config["paths"] = content
            elif json_file.name == "values_pathDefaults.json":
                final_config["pathDefaults"] = content
            else:
                # Все остальные файлы (auth.json, values_app.json, values_rtsp.json...)
                # содержат ключи верхнего уровня и должны быть объединены.
                final_config.update(content)
        # ----------------------------------------------------

        # Write final YAML
        try:
            with open(YAML_FILE, "w", encoding="utf-8") as f:
                yaml.dump(final_config, f, default_flow_style=False, sort_keys=False)
            logger.info(f"Configuration successfully saved to {YAML_FILE}")
        except (IOError, yaml.YAMLError):
            logger.error(f"Failed to write final YAML file.", exc_info=True)
            raise

    except Exception:
        logger.critical(
            "A critical error occurred during the save process.", exc_info=True
        )
        raise
