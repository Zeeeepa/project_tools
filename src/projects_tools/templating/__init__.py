"""
Templating module for project_tools.

This module provides enhanced templating capabilities inspired by AppDaemon's
component generation system, allowing for template inheritance, component
generation, and advanced variable substitution.
"""

from .template_manager import TemplateManager
from .component_generator import ComponentGenerator
from .template_context import TemplateContext
from .deployment_manager import DeploymentManager

__all__ = ['TemplateManager', 'ComponentGenerator', 'TemplateContext', 'DeploymentManager']
