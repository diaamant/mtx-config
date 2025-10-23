"""Tests for config clients."""

import json
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

from src.clients.config_clients import get_config_client
from src.clients.yaml_client import YAMLClient
from src.clients.json_client import JSONClient
from src.core.config import get_settings


class TestJSONClient:
    """Tests for JSONClient."""

    @pytest.fixture
    def temp_json_dir(self, tmp_path):
        """Create temporary JSON directory with test files."""
        json_dir = tmp_path / "json"
        json_dir.mkdir(parents=True)

        # Create test JSON files
        (json_dir / "paths.json").write_text(
            json.dumps({"stream1": {"source": "rtsp://test", "rtspTransport": "tcp"}})
        )
        (json_dir / "values_app.json").write_text(json.dumps({"logLevel": "info"}))
        (json_dir / "empty.json").write_text("")  # Empty file test

        return json_dir

    @patch("src.clients.json_client.get_settings_func")
    def test_load_config_success(self, mock_get_settings, temp_json_dir):
        """Test successful loading of JSON files."""
        mock_settings = MagicMock()
        mock_settings.MTX_JSON_DIR = temp_json_dir
        mock_get_settings.return_value = mock_settings

        client = JSONClient()
        data = client.load_config()

        assert "paths.json" in data
        assert "values_app.json" in data
        assert "paths.json_enabled" in data
        assert "values_app.json_enabled" in data
        assert data["paths.json"] == {
            "stream1": {"source": "rtsp://test", "rtspTransport": "tcp"}
        }
        assert data["values_app.json"] == {"logLevel": "info"}

    @patch("src.clients.json_client.get_settings_func")
    def test_load_config_nonexistent_dir(self, mock_get_settings):
        """Test loading when directory doesn't exist."""
        mock_settings = MagicMock()
        mock_settings.MTX_JSON_DIR = Path("/nonexistent")
        mock_get_settings.return_value = mock_settings

        client = JSONClient()
        data = client.load_config()

        assert data == {}

    @patch("src.clients.json_client.get_settings_func")
    def test_load_config_empty_file(self, mock_get_settings, temp_json_dir):
        """Test loading with empty JSON file."""
        mock_settings = MagicMock()
        mock_settings.MTX_JSON_DIR = temp_json_dir
        mock_get_settings.return_value = mock_settings

        client = JSONClient()
        data = client.load_config()

        # Empty file should not be included
        assert "empty.json" not in data

    @patch("src.clients.json_client.get_settings_func")
    def test_save_config_success(self, mock_get_settings, temp_json_dir):
        """Test successful saving of JSON files."""
        mock_settings = MagicMock()
        mock_settings.MTX_JSON_DIR = temp_json_dir
        mock_get_settings.return_value = mock_settings

        client = JSONClient()
        test_data = {
            "paths.json": {"stream1": {"source": "rtsp://new", "rtspTransport": "udp"}},
            "values_app.json": {"logLevel": "debug"},
            "new_file.json": {"new": "data"},
        }

        client.save_config(test_data)

        # Check files were created/updated
        paths_file = temp_json_dir / "paths.json"
        assert paths_file.exists()
        with open(paths_file) as f:
            saved_data = json.load(f)
        assert saved_data == {
            "stream1": {"source": "rtsp://new", "rtspTransport": "udp"}
        }

        new_file = temp_json_dir / "new_file.json"
        assert new_file.exists()
        with open(new_file) as f:
            saved_data = json.load(f)
        assert saved_data == {"new": "data"}


class TestYAMLClient:
    """Tests for YAMLClient."""

    @pytest.fixture
    def temp_work_dir(self, tmp_path):
        """Create temporary work directory with JSON and YAML files."""
        work_dir = tmp_path / "work"
        json_dir = work_dir / "json"
        json_dir.mkdir(parents=True)

        # Create test JSON files
        (json_dir / "paths.json").write_text(
            json.dumps({"stream1": {"source": "rtsp://test"}})
        )
        (json_dir / "values_app.json").write_text(json.dumps({"logLevel": "info"}))

        # Create YAML file and backup
        yaml_file = work_dir / "mediamtx01.yml"
        yaml_backup = work_dir / "mediamtx01.yml.bak"
        yaml_file.write_text("original yaml content")
        yaml_backup.write_text("original backup")

        return work_dir, json_dir, yaml_file, yaml_backup

    @patch("src.clients.yaml_client.get_settings_func")
    @patch("src.clients.yaml_client.JSONClient")
    def test_save_config_success(
        self, mock_json_client_class, mock_get_settings, temp_work_dir
    ):
        """Test successful YAML saving."""
        work_dir, json_dir, yaml_file, yaml_backup = temp_work_dir

        mock_settings = MagicMock()
        mock_settings.MTX_JSON_DIR = json_dir
        mock_settings.MTX_YAML_FILE = yaml_file
        mock_settings.MTX_YAML_BACKUP_FILE = yaml_backup
        mock_get_settings.return_value = mock_settings

        # Mock JSONClient
        mock_json_client = MagicMock()
        mock_json_client_class.return_value = mock_json_client

        client = YAMLClient()
        test_data = {
            "paths.json": {"stream1": {"source": "rtsp://test"}},
            "values_app.json": {"logLevel": "info"},
            "paths.json_enabled": True,
            "values_app.json_enabled": True,
        }

        client.save_config(test_data)

        # Check backup was created
        assert yaml_backup.exists()
        assert "original yaml content" in yaml_backup.read_text()

        # Check YAML file was updated
        assert yaml_file.exists()
        yaml_content = yaml_file.read_text()
        assert "original yaml content" not in yaml_content
        assert "paths:" in yaml_content
        assert "logLevel" in yaml_content

    @patch("src.clients.yaml_client.get_settings_func")
    def test_save_config_disabled_sections(self, mock_get_settings, temp_work_dir):
        """Test saving with disabled sections."""
        work_dir, json_dir, yaml_file, yaml_backup = temp_work_dir

        mock_settings = MagicMock()
        mock_settings.MTX_JSON_DIR = json_dir
        mock_settings.MTX_YAML_FILE = yaml_file
        mock_settings.MTX_YAML_BACKUP_FILE = yaml_backup
        mock_get_settings.return_value = mock_settings

        client = YAMLClient()
        test_data = {
            "paths.json": {"stream1": {"source": "rtsp://test"}},
            "values_app.json": {"logLevel": "info"},
            "paths.json_enabled": False,  # Disabled
            "values_app.json_enabled": True,
        }

        client.save_config(test_data)

        yaml_content = yaml_file.read_text()
        assert "stream1" not in yaml_content  # Disabled section
        assert "logLevel" in yaml_content  # Enabled section

    @patch("src.clients.yaml_client.get_settings_func")
    def test_load_config_not_implemented(self, mock_get_settings):
        """Test that load_config raises NotImplementedError."""
        mock_settings = MagicMock()
        mock_get_settings.return_value = mock_settings

        client = YAMLClient()

        with pytest.raises(NotImplementedError):
            client.load_config()


class TestGetConfigClient:
    """Tests for get_config_client factory function."""

    def test_get_json_client(self):
        """Test getting JSON client."""
        client = get_config_client("JSON")
        assert isinstance(client, JSONClient)

    def test_get_yaml_client(self):
        """Test getting YAML client."""
        client = get_config_client("YAML")
        assert isinstance(client, YAMLClient)

    def test_unsupported_provider(self):
        """Test unsupported provider raises ValueError."""
        with pytest.raises(ValueError, match="Unsupported provider"):
            get_config_client("UNSUPPORTED")

    def test_caching(self):
        """Test that clients are cached."""
        client1 = get_config_client("JSON")
        client2 = get_config_client("JSON")
        assert client1 is client2  # Same instance due to @lru_cache
