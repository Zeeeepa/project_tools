"""
Projects Tools: A tool for managing projects.

This package provides tools for creating and managing projects, including:
- Project creation with frontend and backend components
- LLM-assisted code generation and analysis
- Project analysis and visualization
- Configuration management
"""

# Initialize logging
from .utils.logging import configure_logging
from .version import __version__

configure_logging()

# Don't import CLI commands here to avoid circular imports
# These will be imported when needed

__all__ = ["__version__"]
