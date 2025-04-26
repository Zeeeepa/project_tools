"""
Tests for the configuration module.
"""

import os
import tempfile
from pathlib import Path

import pytest

from projects_tools.utils.config import DEFAULT_CONFIG, Config


@pytest.fixture(autouse=True)
def reset_config_state():
    """Reset any global state before each test."""
    # Save original state
    original_environ = os.environ.copy()

    # Yield control to the test
    yield

    # Restore original state
    os.environ.clear()
    os.environ.update(original_environ)


@pytest.fixture
def fresh_config():
    """Return a fresh Config instance for each test."""
    # Create a new config with a deep copy of the default config
    config = Config()
    config._config = {k: v.copy() if isinstance(v, dict) else v for k, v in DEFAULT_CONFIG.items()}
    return config


def test_config_init(fresh_config):
    """Test that Config initializes with default values."""
    config = fresh_config
    assert config._config is not None
    assert "llm" in config._config
    assert "project" in config._config
    assert "frontend" in config._config
    assert "backend" in config._config


def test_config_get(fresh_config):
    """Test getting configuration values."""
    config = fresh_config

    # Test getting existing values
    assert config.get("llm.default_provider") == "openai"
    assert config.get("project.default_frontend") == "reactjs"

    # Test getting non-existent values
    assert config.get("non_existent_key") is None
    assert config.get("non_existent_key", "default") == "default"


def test_config_set(fresh_config):
    """Test setting configuration values."""
    config = fresh_config

    # Test setting a new value
    config.set("test.key", "value")
    assert config.get("test.key") == "value"

    # Test overwriting an existing value
    config.set("llm.default_provider", "anthropic")
    assert config.get("llm.default_provider") == "anthropic"

    # Test setting a nested value
    config.set("test.nested.key", "nested_value")
    assert config.get("test.nested.key") == "nested_value"


def test_config_update_from_dict(fresh_config):
    """Test updating configuration from a dictionary."""
    config = fresh_config

    # Test updating with a simple dictionary
    config.update_from_dict({"test": {"key": "value"}})
    assert config.get("test.key") == "value"

    # Test updating with a nested dictionary
    config.update_from_dict({"test": {"nested": {"key": "nested_value"}}})
    assert config.get("test.nested.key") == "nested_value"

    # Test that existing values are preserved
    assert config.get("llm.default_provider") == "openai"


def test_config_load_from_file(fresh_config):
    """Test loading configuration from a file."""
    config = fresh_config

    # Create a temporary file with configuration
    with tempfile.NamedTemporaryFile(mode="w", delete=False) as f:
        f.write('{"test": {"key": "value"}}')
        file_path = f.name

    try:
        # Test loading from the file
        assert config.load_from_file(file_path)
        assert config.get("test.key") == "value"

        # Test that existing values are preserved
        assert config.get("llm.default_provider") == "openai"
    finally:
        # Clean up
        os.unlink(file_path)


def test_config_save_to_file(fresh_config):
    """Test saving configuration to a file."""
    config = fresh_config

    # Set a test value
    config.set("test.key", "value")

    # Create a temporary file
    with tempfile.NamedTemporaryFile(delete=False) as f:
        file_path = f.name

    try:
        # Test saving to the file
        assert config.save_to_file(file_path)

        # Test loading from the file
        new_config = Config()
        assert new_config.load_from_file(file_path)
        assert new_config.get("test.key") == "value"
        assert new_config.get("llm.default_provider") == "openai"
    finally:
        # Clean up
        os.unlink(file_path)


def test_config_load_from_env(fresh_config):
    """Test loading configuration from environment variables."""
    config = fresh_config

    # Set environment variables
    os.environ["PROJECTS_TOOLS_TEST__KEY"] = "value"
    os.environ["PROJECTS_TOOLS_LLM__DEFAULT_PROVIDER"] = "anthropic"

    # Test loading from environment variables
    assert config.load_from_env()
    assert config.get("test.key") == "value"
    assert config.get("llm.default_provider") == "anthropic"


def test_config_as_dict(fresh_config):
    """Test getting the configuration as a dictionary."""
    config = fresh_config

    # Set a test value
    config.set("test.key", "value")

    # Test getting the configuration as a dictionary
    config_dict = config.as_dict()
    assert isinstance(config_dict, dict)
    assert "test" in config_dict
    assert "key" in config_dict["test"]
    assert config_dict["test"]["key"] == "value"
