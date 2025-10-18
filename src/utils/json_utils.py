import json
import shutil
from pathlib import Path
import yaml
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Define paths
WORK_DIR = Path("work")
JSON_DIR = WORK_DIR / "json"
YAML_FILE = WORK_DIR / "mediamtx01.yml"
YAML_BACKUP_FILE = WORK_DIR / "mediamtx01.yml.bak"


from config_models import MODEL_MAPPING
from pydantic import ValidationError

def load_data():
    """Load all JSON files into the data dictionary with error handling and validation."""
    data = {}
    if not JSON_DIR.exists():
        logger.error(f"JSON directory not found: {JSON_DIR}")
        return data

    for json_file in JSON_DIR.glob("*.json"):
        try:
            with open(json_file, "r", encoding='utf-8') as f:
                content = json.load(f)
                
            # Validate content with the corresponding Pydantic model
            model = MODEL_MAPPING.get(json_file.name)
            if model:
                if json_file.name == "paths.json":
                    # Special case for paths, which is a dict of Path models
                    validated_content = {k: model.parse_obj(v) for k, v in content.items()}
                    data[json_file.name] = {k: v.dict(by_alias=True) for k, v in validated_content.items()}
                else:
                    validated_content = model.parse_obj(content)
                    data[json_file.name] = validated_content.dict(by_alias=True)
            else:
                data[json_file.name] = content # No model found, load as is

            data[f"{json_file.name}_enabled"] = True
        except json.JSONDecodeError:
            logger.error(f"Error decoding JSON from {json_file}", exc_info=True)
        except ValidationError as e:
            logger.error(f"Validation error for {json_file}: {e}")
        except IOError:
            logger.error(f"Error reading file {json_file}", exc_info=True)
            
    logger.info("Configuration data loaded and validated successfully.")
    return data


def save_data(data):
    """Save all data back to JSON files and generate the YAML with error handling."""
    try:
        # Save data to JSON files
        for json_file_name, content in data.items():
            if not json_file_name.endswith("_enabled"):
                try:
                    with open(JSON_DIR / json_file_name, "w", encoding='utf-8') as f:
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

        # Assemble the final YAML
        final_config = {}
        for json_file in sorted(JSON_DIR.glob("*.json")):
            if not data.get(f"{json_file.name}_enabled", True):
                logger.info(f"Skipping disabled section: {json_file.name}")
                continue
            
            # Content is already in `data`, no need to re-read
            content = data.get(json_file.name, {})
            
            if json_file.name == "paths.json":
                if 'paths' not in final_config:
                    final_config['paths'] = {}
                final_config['paths'].update(content)
            elif json_file.name.startswith("values_"):
                key = json_file.name.replace("values_", "").replace(".json", "")
                if key == "app":
                    final_config.update(content)
                else:
                    final_config[key] = content
            else:
                key = json_file.name.replace(".json", "")
                final_config[key] = content

        # The logic for pathDefaults and paths seems redundant if the JSON structure is correct.
        # The document noted this. I am simplifying it.
        if "pathDefaults" in final_config and not final_config["pathDefaults"]:
             final_config["pathDefaults"] = {}
        if "paths" not in final_config:
            final_config["paths"] = {}

        # Write final YAML
        try:
            with open(YAML_FILE, "w", encoding='utf-8') as f:
                yaml.dump(final_config, f, default_flow_style=False, sort_keys=False)
            logger.info(f"Configuration successfully saved to {YAML_FILE}")
        except (IOError, yaml.YAMLError):
            logger.error(f"Failed to write final YAML file.", exc_info=True)
            raise

    except Exception:
        logger.critical("A critical error occurred during the save process.", exc_info=True)
        raise