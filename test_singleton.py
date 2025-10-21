#!/usr/bin/env python3
"""Test script to verify singleton pattern for settings and client caching."""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))


def test_singleton_pattern():
    """Test that settings singleton works correctly."""
    from core.config import get_settings, settings

    # Get settings multiple times
    settings1 = get_settings()
    settings2 = get_settings()
    settings3 = settings

    # Check that they are the same object
    assert settings1 is settings2, "get_settings() should return the same instance"
    assert settings1 is settings3, "settings variable should be the same instance"
    assert settings2 is settings3, "All should be the same instance"

    print("✓ Singleton pattern test passed!")
    print(f"Settings instance: {id(settings1)}")
    print(f"Settings DEBUG: {settings1.DEBUG}")
    print(f"Settings app_port: {settings1.app_port}")

    return True


def test_client_caching():
    """Test that config clients are cached correctly."""
    from clients.config_clients import get_config_client

    # Get clients multiple times
    json_client1 = get_config_client("JSON")
    json_client2 = get_config_client("JSON")
    yaml_client1 = get_config_client("YAML")
    yaml_client2 = get_config_client("YAML")

    # Check that they are the same objects (cached)
    assert json_client1 is json_client2, "JSON clients should be cached"
    assert yaml_client1 is yaml_client2, "YAML clients should be cached"
    assert json_client1 is not yaml_client1, (
        "Different client types should be different"
    )

    print("✓ Client caching test passed!")
    print(f"JSON client instance: {id(json_client1)}")
    print(f"YAML client instance: {id(yaml_client1)}")

    return True


if __name__ == "__main__":
    test_singleton_pattern()
    test_client_caching()
    print("✓ All tests passed!")
