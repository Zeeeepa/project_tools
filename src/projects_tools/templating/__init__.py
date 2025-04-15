"""
Templating system for project_tools.

This module provides a templating system for project_tools with advanced
features like inheritance, component generation, and variable substitution.
"""

from .template_context import TemplateContext
from .template_manager import TemplateManager
from .component_generator import ComponentGenerator
from .template_registry import TemplateRegistry
from .pattern_generator import PatternGenerator
from .layout_generator import LayoutGenerator

__all__ = [
    'TemplateContext',
    'TemplateManager',
    'ComponentGenerator',
    'TemplateRegistry',
    'PatternGenerator',
    'LayoutGenerator'
]
