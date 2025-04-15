"""
Configuration management for projects_tools.

This module provides a centralized configuration system that supports loading
configuration from environment variables, configuration files, and CLI arguments.
"""

import os
import json
import logging
from pathlib import Path
from typing import Any, Dict, Optional, Union

logger = logging.getLogger(__name__)

# Default configuration values
DEFAULT_CONFIG = {
    # LLM settings
    "llm": {
        "default_provider": "openai",
        "openai": {
            "model": "gpt-4",
            "temperature": 0.7,
            "max_tokens": 1000,
        },
        "anthropic": {
            "model": "claude-3-opus-20240229",
            "temperature": 0.7,
            "max_tokens": 1000,
        },
    },
    # Project settings
    "project": {
        "default_frontend": "reactjs",
        "templates_dir": None,  # Will be set at runtime
    },
    # Frontend settings
    "frontend": {
        "react": {
            "use_typescript": True,
            "use_tailwind": True,
        },
        "vue": {
            "use_typescript": True,
            "use_tailwind": True,
        },
    },
    # Backend settings
    "backend": {
        "python": {
            "min_version": "3.9",
        },
    },
}


class Config:
    """Configuration manager for projects_tools."""

    def __init__(self):
        """Initialize configuration with default values."""
        self._config = DEFAULT_CONFIG.copy()
        self._config_file_path = None
        self._loaded_from_file = False
        self._loaded_from_env = False

    def load_from_file(self, file_path: Optional[Union[str, Path]] = None) -> bool:
        """
        Load configuration from a JSON file.

        Args:
            file_path: Path to the configuration file. If None, will look in
                standard locations.

        Returns:
            Whether the configuration was successfully loaded.
        """
        if file_path is None:
            # Look in standard locations
            locations = [
                Path.cwd() / ".projects_tools.json",
                Path.home() / ".projects_tools.json",
                Path.home() / ".config" / "projects_tools.json",
            ]
            for loc in locations:
                if loc.exists():
                    file_path = loc
                    break
            else:
                logger.debug("No configuration file found in standard locations")
                return False

        try:
            with open(file_path, "r") as f:
                file_config = json.load(f)
            
            # Update configuration with values from file
            self._update_config(file_config)
            self._config_file_path = file_path
            self._loaded_from_file = True
            logger.info(f"Loaded configuration from {file_path}")
            return True
        except Exception as e:
            logger.warning(f"Error loading configuration from {file_path}: {e}")
            return False

    def load_from_env(self) -> bool:
        """
        Load configuration from environment variables.

        Environment variables should be prefixed with PROJECTS_TOOLS_.
        For nested configuration, use double underscore as separator.
        For example, PROJECTS_TOOLS_LLM__DEFAULT_PROVIDER=openai.

        Returns:
            Whether any configuration was loaded from environment variables.
        """
        prefix = "PROJECTS_TOOLS_"
        loaded = False

        for key, value in os.environ.items():
            if key.startswith(prefix):
                # Remove prefix and split by double underscore
                config_key = key[len(prefix):].lower()
                parts = config_key.split("__")
                
                # Convert value to appropriate type
                if value.lower() in ("true", "yes", "1"):
                    value = True
                elif value.lower() in ("false", "no", "0"):
                    value = False
                elif value.isdigit():
                    value = int(value)
                elif value.replace(".", "", 1).isdigit() and value.count(".") == 1:
                    value = float(value)
                
                # Update configuration
                self._set_nested_value(self._config, parts, value)
                loaded = True
        
        self._loaded_from_env = loaded
        if loaded:
            logger.info("Loaded configuration from environment variables")
        return loaded

    def update_from_dict(self, config_dict: Dict[str, Any]) -> None:
        """
        Update configuration from a dictionary.

        Args:
            config_dict: Dictionary with configuration values.
        """
        self._update_config(config_dict)

    def get(self, key: str, default: Any = None) -> Any:
        """
        Get a configuration value.

        Args:
            key: Configuration key, using dot notation for nested values.
            default: Default value to return if key is not found.

        Returns:
            Configuration value or default.
        """
        parts = key.split(".")
        value = self._config
        
        for part in parts:
            if isinstance(value, dict) and part in value:
                value = value[part]
            else:
                return default
        
        return value

    def set(self, key: str, value: Any) -> None:
        """
        Set a configuration value.

        Args:
            key: Configuration key, using dot notation for nested values.
            value: Value to set.
        """
        parts = key.split(".")
        self._set_nested_value(self._config, parts, value)

    def _update_config(self, config_dict: Dict[str, Any]) -> None:
        """
        Update configuration with values from a dictionary.

        Args:
            config_dict: Dictionary with configuration values.
        """
        def update_nested(target, source):
            for key, value in source.items():
                if isinstance(value, dict) and key in target and isinstance(target[key], dict):
                    update_nested(target[key], value)
                else:
                    target[key] = value
        
        update_nested(self._config, config_dict)

    def _set_nested_value(self, config_dict: Dict[str, Any], keys: list, value: Any) -> None:
        """
        Set a nested value in the configuration dictionary.

        Args:
            config_dict: Configuration dictionary.
            keys: List of keys to navigate the nested structure.
            value: Value to set.
        """
        if len(keys) == 1:
            config_dict[keys[0]] = value
            return
        
        key = keys[0]
        if key not in config_dict:
            config_dict[key] = {}
        
        if not isinstance(config_dict[key], dict):
            config_dict[key] = {}
        
        self._set_nested_value(config_dict[key], keys[1:], value)

    def save_to_file(self, file_path: Optional[Union[str, Path]] = None) -> bool:
        """
        Save configuration to a JSON file.

        Args:
            file_path: Path to the configuration file. If None, will use the
                file path from which the configuration was loaded, or the default
                location.

        Returns:
            Whether the configuration was successfully saved.
        """
        if file_path is None:
            if self._config_file_path is not None:
                file_path = self._config_file_path
            else:
                file_path = Path.home() / ".projects_tools.json"
        
        try:
            with open(file_path, "w") as f:
                json.dump(self._config, f, indent=2)
            
            logger.info(f"Saved configuration to {file_path}")
            return True
        except Exception as e:
            logger.warning(f"Error saving configuration to {file_path}: {e}")
            return False

    def as_dict(self) -> Dict[str, Any]:
        """
        Get the configuration as a dictionary.

        Returns:
            Configuration dictionary.
        """
        return self._config.copy()


# Global configuration instance
config = Config()

# Initialize configuration
def init_config():
    """Initialize configuration from files and environment variables."""
    # Load from file first, then override with environment variables
    config.load_from_file()
    config.load_from_env()
    
    # Set runtime values
    if config.get("project.templates_dir") is None:
        import pkg_resources
        templates_dir = pkg_resources.resource_filename("projects_tools", "templates")
        config.set("project.templates_dir", templates_dir)

# Initialize configuration when module is imported
init_config()
