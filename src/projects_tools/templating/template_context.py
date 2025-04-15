"""
Template context for project_tools.

This module provides a context class for template rendering, allowing for
variable substitution, inheritance, and advanced features.
"""

import os
import json
from typing import Dict, Any, Optional, List, Union
from jinja2 import Environment, PackageLoader, FileSystemLoader, select_autoescape, Template


class TemplateContext:
    """
    A class to manage template context variables and provide helper methods
    for template rendering.
    
    This class is inspired by AppDaemon's templating system and provides
    advanced features like variable mapping, inheritance, and component
    generation.
    """
    
    def __init__(self, base_context: Optional[Dict[str, Any]] = None):
        """
        Initialize a new template context.
        
        Args:
            base_context: Optional base context dictionary to initialize with
        """
        self.context = base_context or {}
        self.parent_contexts = []
        self._filters = {}
        
    def add_filter(self, name: str, filter_func):
        """
        Add a custom filter to the context.
        
        Args:
            name: Name of the filter
            filter_func: Filter function
        """
        self._filters[name] = filter_func
        
    def apply_filters_to_env(self, env: Environment):
        """
        Apply all registered filters to a Jinja2 environment.
        
        Args:
            env: Jinja2 Environment to apply filters to
        """
        for name, func in self._filters.items():
            env.filters[name] = func
    
    def set(self, key: str, value: Any):
        """
        Set a context variable.
        
        Args:
            key: Variable name
            value: Variable value
        """
        self.context[key] = value
        
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get a context variable.
        
        Args:
            key: Variable name
            default: Default value if not found
            
        Returns:
            The variable value or default
        """
        return self.context.get(key, default)
    
    def update(self, values: Dict[str, Any]):
        """
        Update the context with multiple values.
        
        Args:
            values: Dictionary of values to update
        """
        self.context.update(values)
        
    def inherit_from(self, parent_context: 'TemplateContext'):
        """
        Inherit from a parent context.
        
        Args:
            parent_context: Parent context to inherit from
        """
        self.parent_contexts.append(parent_context)
        
    def get_merged_context(self) -> Dict[str, Any]:
        """
        Get the merged context including all parent contexts.
        
        Returns:
            Merged context dictionary
        """
        result = {}
        
        # Apply parent contexts in order
        for parent in self.parent_contexts:
            result.update(parent.get_merged_context())
            
        # Apply own context last to override parent values
        result.update(self.context)
        
        return result
    
    def load_from_json(self, json_file: str):
        """
        Load context from a JSON file.
        
        Args:
            json_file: Path to JSON file
        """
        if os.path.exists(json_file):
            with open(json_file, 'r') as f:
                data = json.load(f)
                self.update(data)
                
    def save_to_json(self, json_file: str):
        """
        Save context to a JSON file.
        
        Args:
            json_file: Path to JSON file
        """
        with open(json_file, 'w') as f:
            json.dump(self.context, f, indent=2)
            
    def render_string(self, template_string: str, env: Optional[Environment] = None) -> str:
        """
        Render a template string with the current context.
        
        Args:
            template_string: Template string to render
            env: Optional Jinja2 environment
            
        Returns:
            Rendered string
        """
        if env is None:
            env = Environment(autoescape=select_autoescape(['html', 'xml']))
            self.apply_filters_to_env(env)
            
        template = env.from_string(template_string)
        return template.render(**self.get_merged_context())
    
    def __contains__(self, key: str) -> bool:
        """
        Check if a key exists in the context.
        
        Args:
            key: Key to check
            
        Returns:
            True if key exists, False otherwise
        """
        if key in self.context:
            return True
            
        # Check parent contexts
        for parent in self.parent_contexts:
            if key in parent:
                return True
                
        return False
