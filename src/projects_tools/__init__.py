"""
Projects Tools: A tool for managing projects.

This package provides tools for creating and managing projects, including:
- Project creation with frontend and backend components
- LLM-assisted code generation and analysis
- Project analysis and visualization
- Configuration management
"""

from .version import __version__

# Initialize logging
from .utils.logging import configure_logging
configure_logging()

# Import main CLI entry point
from .cli.commands import cli, main

__all__ = ["__version__", "cli", "main"]
