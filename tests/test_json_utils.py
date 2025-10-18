import pytest
import os
import json
from pathlib import Path
from src.utils.json_utils import load_data, save_data


# Create a fixture for a temporary work directory
@pytest.fixture
def temp_work_dir(tmp_path):
    work_dir = tmp_path / "work"
    json_dir = work_dir / "json"
    json_dir.mkdir(parents=True)

    # Create dummy json files
    (json_dir / "paths.json").write_text(
        json.dumps({"test_path": {"source": "rtsp://localhost"}})
    )
    (json_dir / "values_app.json").write_text(json.dumps({"logLevel": "info"}))

    # Monkeypatch the paths in json_utils
    original_work_dir = "src.utils.json_utils.WORK_DIR"
    original_json_dir = "src.utils.json_utils.JSON_DIR"

    with pytest.MonkeyPatch.context() as m:
        m.setattr(original_work_dir, work_dir)
        m.setattr(original_json_dir, json_dir)
        yield work_dir


def test_load_data_creates_enabled_flags(temp_work_dir):
    """
    Tests that load_data correctly loads json files and adds the '_enabled' flag.
    """
    data = load_data()

    assert "paths.json" in data
    assert "paths.json_enabled" in data
    assert data["paths.json_enabled"] is True

    assert "values_app.json" in data
    assert "values_app.json_enabled" in data
    assert data["values_app.json_enabled"] is True


def test_save_data_creates_yaml_and_backup(temp_work_dir):
    """
    Tests that save_data correctly creates the YAML file and a backup.
    """
    # Load initial data
    data = load_data()

    # Create a dummy original yaml to be backed up
    yaml_file = temp_work_dir / "mediamtx01.yml"
    yaml_file.write_text("original_content")

    # Save the data
    save_data(data)

    # Check that the yaml file was created/updated
    assert yaml_file.exists()
    assert "original_content" not in yaml_file.read_text()
    assert "paths:" in yaml_file.read_text()

    # Check that the backup was created
    backup_file = temp_work_dir / "mediamtx01.yml.bak"
    assert backup_file.exists()
    assert "original_content" in backup_file.read_text()


def test_save_data_skips_disabled_sections(temp_work_dir):
    """
    Tests that save_data correctly skips sections that are disabled.
    """
    data = load_data()

    # Disable the 'paths.json' section
    data["paths.json_enabled"] = False

    save_data(data)

    yaml_file = temp_work_dir / "mediamtx01.yml"
    yaml_content = yaml_file.read_text()

    # The 'paths' key should be empty or not present
    assert "test_path" not in yaml_content
    # The 'app' section should still be present
    assert "logLevel" in yaml_content
