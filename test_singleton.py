#!/usr/bin/env python3
"""Test script to verify singleton pattern for settings."""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

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

if __name__ == "__main__":
    test_singleton_pattern()
