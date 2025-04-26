"""
Tests for the configuration module.
"""

import os
import tempfile
from pathlib import Path

import pytest

from projects_tools.utils.config import Config


def test_config_init():
    """Test that Config initializes with default values."""
    config = Config()
    assert config._config is not None
    assert "llm" in config._config
    assert "project" in config._config
    assert "frontend" in config._config
    assert "backend" in config._config


def test_config_get():
    """Test getting configuration values."""
    config = Config()
    
    # Test getting existing values
    assert config.get("llm.default_provider") == "openai"
    assert config.get("project.default_frontend") == "reactjs"
    
    # Test getting non-existent values
    assert config.get("non_existent_key") is None
    assert config.get("non_existent_key", "default") == "default"


def test_config_set():
    """Test setting configuration values."""
    config = Config()
    
    # Test setting a new value
    config.set("test.key", "value")
    assert config.get("test.key") == "value"
    
    # Test overwriting an existing value
    config.set("llm.default_provider", "anthropic")
    assert config.get("llm.default_provider") == "anthropic"
    
    # Test setting a nested value
    config.set("test.nested.key", "nested_value")
    assert config.get("test.nested.key") == "nested_value"


def test_config_update_from_dict():
    """Test updating configuration from a dictionary."""
    config = Config()
    
    # Test updating with a simple dictionary
    config.update_from_dict({"test": {"key": "value"}})
    assert config.get("test.key") == "value"
    
    # Test updating with a nested dictionary
    config.update_from_dict({"test": {"nested": {"key": "nested_value"}}})
    assert config.get("test.nested.key") == "nested_value"
    
    # Test that existing values are preserved
    assert "llm" in config.as_dict()
    assert "default_provider" in config.as_dict()["llm"]


def test_config_load_from_file():
    """Test loading configuration from a file."""
    config = Config()
    
    # Create a temporary file with configuration
    with tempfile.NamedTemporaryFile(mode="w", delete=False) as f:
        f.write('{"test": {"key": "value"}}')
        file_path = f.name
    
    try:
        # Test loading from the file
        assert config.load_from_file(file_path)
        assert config.get("test.key") == "value"
        
        # Test that existing values are preserved
        assert "llm" in config.as_dict()
        assert "default_provider" in config.as_dict()["llm"]
    finally:
        # Clean up
        os.unlink(file_path)


def test_config_save_to_file():
    """Test saving configuration to a file."""
    config = Config()
    
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
        assert "llm" in new_config.as_dict()
        assert "default_provider" in new_config.as_dict()["llm"]
    finally:
        # Clean up
        os.unlink(file_path)


def test_config_load_from_env():
    """Test loading configuration from environment variables."""
    config = Config()
    
    # Set environment variables
    os.environ["PROJECTS_TOOLS_TEST__KEY"] = "value"
    os.environ["PROJECTS_TOOLS_LLM__DEFAULT_PROVIDER"] = "anthropic"
    
    try:
        # Test loading from environment variables
        assert config.load_from_env()
        assert config.get("test.key") == "value"
        assert config.get("llm.default_provider") == "anthropic"
    finally:
        # Clean up
        del os.environ["PROJECTS_TOOLS_TEST__KEY"]
        del os.environ["PROJECTS_TOOLS_LLM__DEFAULT_PROVIDER"]


def test_config_as_dict():
    """Test getting the configuration as a dictionary."""
    config = Config()
    
    # Set a test value
    config.set("test.key", "value")
    
    # Test getting the configuration as a dictionary
    config_dict = config.as_dict()
    assert isinstance(config_dict, dict)
    assert "test" in config_dict
    assert "key" in config_dict["test"]
    assert config_dict["test"]["key"] == "value"
