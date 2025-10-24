"""Tests for import/export functionality."""

from src.service.mtx_manager import MtxConfigManager
from src.clients.yaml_client import YAMLClient


def test_yaml_client_export_import_roundtrip():
    """Test that export and import produce equivalent results."""

    # Initialize manager and load current data
    manager = MtxConfigManager()
    manager.load_data()

    # Export current configuration
    yaml_content = manager.export_config()

    # Import the configuration back
    manager.import_config(yaml_content)

    # Export again and compare
    yaml_content_2 = manager.export_config()

    # The YAML strings should be identical
    assert yaml_content == yaml_content_2, "Export/Import roundtrip failed"

    print("✅ Export/Import roundtrip test passed")


def test_yaml_client_structure_conversion():
    """Test conversion between internal and YAML formats."""

    yaml_client = YAMLClient()

    # Sample internal data structure
    internal_data = {
        "values_app.json": {"logLevel": "info", "readTimeout": "10s"},
        "auth.json": {"internal": True, "external": False},
        "paths.json": {"stream1": {"source": "rtsp://test", "name": "test_stream"}},
    }

    # Convert to YAML structure
    yaml_structure = yaml_client._convert_to_yaml_structure(internal_data)

    # Expected YAML structure
    expected_yaml = {
        "app": {"logLevel": "info", "readTimeout": "10s"},
        "auth": {"internal": True, "external": False},
        "paths": {"stream1": {"source": "rtsp://test", "name": "test_stream"}},
    }

    assert yaml_structure == expected_yaml, "YAML structure conversion failed"

    # Convert back to internal structure
    internal_structure = yaml_client._convert_from_yaml_structure(yaml_structure)

    assert internal_structure == internal_data, "Internal structure conversion failed"

    print("✅ Structure conversion test passed")


def test_import_validation():
    """Test import validation functionality."""

    manager = MtxConfigManager()

    # Test with invalid YAML
    try:
        # Using a string that's not valid YAML
        manager.import_config("this is not valid yaml: [")
        assert False, "Should have raised ValueError for invalid YAML"
    except ValueError as e:
        print(f"✅ Invalid YAML validation test passed: {str(e)[:50]}...")

    # Test with empty dict
    try:
        manager.import_config("{}")
        assert False, "Should have raised ValueError for missing required sections"
    except ValueError:
        print("✅ Missing sections validation test passed")


if __name__ == "__main__":
    print("Running import/export tests...")

    try:
        test_yaml_client_structure_conversion()
        test_import_validation()

        print("\n🎉 All tests passed!")
        print("\nTo test with real data:")
        print("1. Run the application")
        print("2. Click Export button to download current config")
        print("3. Modify the downloaded YAML file")
        print("4. Click Import button and upload the modified file")
        print("5. Verify that the UI reflects the imported changes")

    except Exception as e:
        print(f"❌ Test failed: {e}")
        raise
