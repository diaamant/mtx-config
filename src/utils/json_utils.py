import json
import logging
import shutil
from pathlib import Path
import inspect  # <-- Добавлено

import yaml

from core.config import settings
from models.config_models import MODEL_MAPPING
from pydantic import ValidationError, BaseModel  # <-- Добавлен BaseModel

# Set up logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Define paths
# WORK_DIR = Path("work")
WORK_DIR = settings.MTX_WORK_DIR
JSON_DIR = settings.MTX_JSON_DIR
YAML_FILE = settings.MTX_YAML_FILE
YAML_BACKUP_FILE = settings.MTX_YAML_BACKUP_FILE


def load_data():
    """Load all JSON files into the data dictionary with error handling and validation."""
    data = {}
    if not JSON_DIR.exists():
        logger.error(f"JSON directory not found: {JSON_DIR}")
        return data

    for json_file in JSON_DIR.glob("*.json"):
        try:
            with open(json_file, "r", encoding="utf-8") as f:
                content = json.load(f)
                if not content:  # Пропускаем пустые файлы
                    logger.warning(f"File {json_file.name} is empty, skipping.")
                    continue

            # Validate content with the corresponding Pydantic model
            model = MODEL_MAPPING.get(json_file.name)

            # --- ИСПРАВЛЕНИЕ 1: Явная проверка, что model - это Pydantic-модель ---
            is_valid_model = (
                model and inspect.isclass(model) and issubclass(model, BaseModel)
            )
            # ---------------------------------------------------------------------

            if is_valid_model:
                if json_file.name == "paths.json":
                    # Special case for paths, which is a dict of Path models
                    validated_content = {
                        k: model.parse_obj(v) for k, v in content.items()
                    }
                    data[json_file.name] = {
                        k: v.dict(by_alias=True) for k, v in validated_content.items()
                    }
                else:
                    validated_content = model.parse_obj(content)
                    data[json_file.name] = validated_content.dict(by_alias=True)
            else:
                if model and model is dict:
                    logger.warning(
                        f"Model for {json_file.name} is 'dict', loading as is."
                    )
                data[json_file.name] = content  # No model found, load as is

            data[f"{json_file.name}_enabled"] = True

        except json.JSONDecodeError:
            logger.error(f"Error decoding JSON from {json_file}", exc_info=True)
        except ValidationError as e:
            logger.error(f"Validation error for {json_file}: {e}")
        except IOError:
            logger.error(f"Error reading file {json_file}", exc_info=True)
        except Exception as e:
            # Ловим другие неожиданные ошибки при обработке файла
            logger.error(f"Unexpected error processing {json_file}: {e}", exc_info=True)

    logger.info("Configuration data loaded and validated successfully.")
    return data


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
