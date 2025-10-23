import pytest
import json
from pathlib import Path
from unittest.mock import patch, MagicMock

from src.clients.config_clients import get_config_client


@pytest.fixture
def temp_work_dir(tmp_path):
    """Create temporary work directory with JSON files."""
    work_dir = tmp_path / "work"
    json_dir = work_dir / "json"
    json_dir.mkdir(parents=True)

    # Create dummy json files
    (json_dir / "paths.json").write_text(
        json.dumps({"test_path": {"source": "rtsp://localhost"}})
    )
    (json_dir / "values_app.json").write_text(json.dumps({"logLevel": "info"}))

    # Create a dummy original yaml to be backed up
    yaml_file = work_dir / "mediamtx01.yml"
    yaml_file.write_text("original_content")

    return work_dir, json_dir, yaml_file


@patch("src.clients.yaml_client.get_settings_func")
@patch("src.clients.json_client.get_settings_func")
@patch("src.clients.yaml_client.JSONClient")
def test_load_data_creates_enabled_flags(
    mock_json_client_class,
    mock_json_get_settings,
    mock_yaml_get_settings,
    temp_work_dir,
):
    """Tests that load_data correctly loads json files and adds the '_enabled' flag."""
    work_dir, json_dir, yaml_file = temp_work_dir

    # Clear the client cache
    from src.clients.config_clients import get_config_client

    get_config_client.cache_clear()

    mock_settings = MagicMock()
    mock_settings.MTX_JSON_DIR = json_dir
    mock_json_get_settings.return_value = mock_settings
    mock_yaml_get_settings.return_value = mock_settings

    # Mock JSONClient
    mock_json_client = MagicMock()
    mock_json_client_class.return_value = mock_json_client

    # Use JSONClient instead of old load_data function
    json_client = get_config_client("JSON")
    data = json_client.load_config()

    assert "paths.json" in data
    assert "paths.json_enabled" in data
    assert data["paths.json_enabled"] is True

    assert "values_app.json" in data
    assert "values_app.json_enabled" in data
    assert data["values_app.json_enabled"] is True


@patch("src.clients.yaml_client.get_settings_func")
@patch("src.clients.json_client.get_settings_func")
@patch("src.clients.yaml_client.JSONClient")
def test_save_data_creates_yaml_and_backup(
    mock_json_client_class,
    mock_json_get_settings,
    mock_yaml_get_settings,
    temp_work_dir,
):
    """Tests that save_data correctly creates the YAML file and a backup."""
    work_dir, json_dir, yaml_file = temp_work_dir

    # Clear the client cache
    from src.clients.config_clients import get_config_client

    get_config_client.cache_clear()

    mock_settings = MagicMock()
    mock_settings.MTX_JSON_DIR = json_dir
    mock_settings.MTX_YAML_FILE = yaml_file
    mock_settings.MTX_YAML_BACKUP_FILE = yaml_file.with_suffix(".yml.bak")
    mock_json_get_settings.return_value = mock_settings
    mock_yaml_get_settings.return_value = mock_settings

    # Mock JSONClient
    mock_json_client = MagicMock()
    mock_json_client_class.return_value = mock_json_client
    mock_json_client.save_config.return_value = None  # Do nothing for JSON save

    # Create test data
    data = {
        "paths.json": {"test_path": {"source": "rtsp://localhost"}},
        "values_app.json": {"logLevel": "info"},
        "paths.json_enabled": True,
        "values_app.json_enabled": True,
    }
    mock_json_client.load_config.return_value = data  # Return test data

    # Load initial data using JSONClient
    json_client = get_config_client("JSON")
    data = json_client.load_config()

    # Use YAMLClient to save data
    yaml_client = get_config_client("YAML")
    yaml_client.save_config(data)

    # Check that the yaml file was created/updated
    assert yaml_file.exists()
    yaml_content = yaml_file.read_text()
    assert "original_content" not in yaml_content
    assert "paths:" in yaml_content

    # Check that the backup was created
    backup_file = work_dir / "mediamtx01.yml.bak"
    assert backup_file.exists()
    assert "original_content" in backup_file.read_text()


@patch("src.clients.yaml_client.get_settings_func")
@patch("src.clients.json_client.get_settings_func")
@patch("src.clients.yaml_client.JSONClient")
def test_save_data_skips_disabled_sections(
    mock_json_client_class,
    mock_json_get_settings,
    mock_yaml_get_settings,
    temp_work_dir,
):
    """Tests that save_data correctly skips sections that are disabled."""
    work_dir, json_dir, yaml_file = temp_work_dir

    # Clear the client cache
    from src.clients.config_clients import get_config_client

    get_config_client.cache_clear()

    mock_settings = MagicMock()
    mock_settings.MTX_JSON_DIR = json_dir
    mock_settings.MTX_YAML_FILE = yaml_file
    mock_settings.MTX_YAML_BACKUP_FILE = yaml_file.with_suffix(".yml.bak")
    mock_json_get_settings.return_value = mock_settings
    mock_yaml_get_settings.return_value = mock_settings

    # Mock JSONClient
    mock_json_client = MagicMock()
    mock_json_client_class.return_value = mock_json_client
    mock_json_client.save_config.return_value = None  # Do nothing for JSON save

    # Create test data
    data = {
        "paths.json": {"test_path": {"source": "rtsp://localhost"}},
        "values_app.json": {"logLevel": "info"},
        "paths.json_enabled": True,
        "values_app.json_enabled": True,
    }
    mock_json_client.load_config.return_value = data  # Return test data

    # Load data and disable a section
    json_client = get_config_client("JSON")
    data = json_client.load_config()
    data["paths.json_enabled"] = False

    # Use YAMLClient to save data
    yaml_client = get_config_client("YAML")
    yaml_client.save_config(data)

    yaml_content = yaml_file.read_text()

    # The 'paths' key should be empty or not present
    assert "test_path" not in yaml_content
    # The 'app' section should still be present
    assert "logLevel" in yaml_content
