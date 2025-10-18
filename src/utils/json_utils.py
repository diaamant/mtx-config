import json
import logging

from core.config import settings
from pydantic import ValidationError  # <-- Добавлен BaseModel

# Set up logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Define paths
# WORK_DIR = Path("work")
WORK_DIR = settings.MTX_WORK_DIR
JSON_DIR = settings.MTX_JSON_DIR


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

            data[json_file.name] = content
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
