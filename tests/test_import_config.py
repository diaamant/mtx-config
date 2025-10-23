"""Tests for config import functionality."""

import os
import json
import pytest
import yaml
from pathlib import Path
from src.mtx_manager import MtxConfigManager

# Get the test data directory
TEST_DIR = Path(__file__).parent
JSON_TEST_DIR = TEST_DIR / "json_test"

# Expected JSON files
EXPECTED_JSON_FILES = [
    "values_app.json",
    "auth.json",
    "paths.json",
    "values_hls.json",
    "values_pathDefaults.json",
    "values_rtmp.json",
    "values_rtsp.json",
    "values_srt.json",
    "values_webrtc.json",
]


def create_test_yaml() -> str:
    """Create a test YAML configuration based on the expected JSON files."""
    config = {}

    # Load all JSON files and merge them into a single config
    for json_file in EXPECTED_JSON_FILES:
        if not json_file.endswith("_enabled"):
            filepath = JSON_TEST_DIR / json_file
            if filepath.exists():
                with open(filepath, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    # Convert JSON filename to YAML section name using the same mapping as YAMLClient
                    section = json_file.replace("values_", "").replace(".json", "")
                    if section == "app":
                        # For app section, all values go to root level
                        config.update(data)
                    else:
                        # For other sections, they become top-level sections in YAML
                        config[section] = data

    return yaml.dump(config, default_flow_style=False)


def load_expected_json(filename: str) -> dict:
    """Load expected JSON data for comparison."""
    filepath = JSON_TEST_DIR / filename
    if not filepath.exists():
        return {}

    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)


class TestImportConfig:
    """Test cases for config import functionality."""

    @pytest.fixture(autouse=True)
    def setup(self, tmp_path):
        """Set up test environment."""
        self.manager = MtxConfigManager(json_dir=tmp_path)
        self.test_yaml = create_test_yaml()
        self.expected_data = {}

        # Load all expected JSON data
        for json_file in EXPECTED_JSON_FILES:
            if not json_file.endswith("_enabled"):
                filepath = JSON_TEST_DIR / json_file
                if filepath.exists():
                    with open(filepath, "r", encoding="utf-8") as f:
                        self.expected_data[json_file] = json.load(f)

    def test_import_config_structure(self):
        """Test that importing YAML produces the expected JSON structure."""
        # Import the test YAML
        self.manager.import_config(self.test_yaml)

        # Get the imported data
        imported_data = self.manager.data

        # Check that all expected JSON files are present
        for json_file in self.expected_data:
            assert json_file in imported_data, (
                f"Missing expected JSON file in imported data: {json_file}"
            )

            # For non-empty expected data, verify the content
            if self.expected_data[json_file]:
                assert imported_data[json_file] == self.expected_data[json_file], (
                    f"Mismatch in {json_file}. Expected: {self.expected_data[json_file]}, Got: {imported_data[json_file]}"
                )

    def test_yaml_import_basic(self):
        """Test basic YAML import functionality."""
        # This should not raise any exceptions
        self.manager.import_config(self.test_yaml)

        # Verify we have some data
        assert self.manager.data, "No data imported"

        # Verify paths.json exists (required by validation)
        assert "paths.json" in self.manager.data, "paths.json is required but missing"
        assert self.manager.data["paths.json"], "paths.json should not be empty"

    def test_import_export_consistency(self):
        """Test that importing and then exporting produces equivalent YAML."""
        # Import the test YAML
        self.manager.import_config(self.test_yaml)

        # Export it back to YAML
        exported_yaml = self.manager.export_config()

        # Import the exported YAML to a new manager
        new_manager = MtxConfigManager()
        new_manager.import_config(exported_yaml)

        # The data should be the same
        assert self.manager.data == new_manager.data, (
            "Imported and exported data do not match"
        )

    def test_import_invalid_yaml(self):
        """Test that invalid YAML raises an appropriate exception."""
        with pytest.raises(ValueError):
            self.manager.import_config("invalid: yaml: {")

    def test_import_empty_config(self):
        """Test that empty config is handled correctly."""
        with pytest.raises(
            ValueError, match="Invalid YAML format: expected a dictionary"
        ):
            self.manager.import_config("")


if __name__ == "__main__":
    pytest.main(["-v", __file__])
