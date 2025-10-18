import json
import shutil
from pathlib import Path
import yaml

# Define paths
WORK_DIR = Path("work")
JSON_DIR = WORK_DIR / "json"
YAML_FILE = WORK_DIR / "mediamtx01.yml"
YAML_BACKUP_FILE = WORK_DIR / "mediamtx01.yml.bak"


def load_data():
    """Load all JSON files into the data dictionary."""
    data = {}
    for json_file in JSON_DIR.glob("*.json"):
        with open(json_file, "r") as f:
            data[json_file.name] = json.load(f)
            data[f"{json_file.name}_enabled"] = True
    return data


def save_data(data):
    """Save all data from the UI back to the JSON files and generate the YAML."""
    # Save data to JSON files
    for json_file_name, content in data.items():
        if not json_file_name.endswith("_enabled"):
            with open(JSON_DIR / json_file_name, "w") as f:
                json.dump(content, f, indent=2)

    # Create backup
    if YAML_FILE.exists():
        shutil.copy(YAML_FILE, YAML_BACKUP_FILE)

    # Assemble the final YAML
    final_config = {}
    for json_file in sorted(JSON_DIR.glob("*.json")):
        if not data.get(f"{json_file.name}_enabled", True):
            continue
        with open(json_file, "r") as f:
            content = json.load(f)
            if json_file.name == "paths.json":
                if "paths" not in final_config:
                    final_config["paths"] = {}
                final_config["paths"].update(content)
            elif json_file.name.startswith("values_"):
                key = json_file.name.replace("values_", "").replace(".json", "")
                if key == "app":
                    final_config.update(content)
                else:
                    final_config[key] = content
            else:
                key = json_file.name.replace(".json", "")
                final_config[key] = content

    # Remap pathDefaults to the correct structure
    if "pathDefaults" in final_config:
        final_config["pathDefaults"] = final_config.get("pathDefaults", {})

    # Ensure paths is a dictionary
    if "paths" not in final_config:
        final_config["paths"] = {}

    with open(YAML_FILE, "w") as f:
        yaml.dump(final_config, f, default_flow_style=False, sort_keys=False)
