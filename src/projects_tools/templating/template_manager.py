"""
Template manager for project_tools.

This module provides a template manager class for loading, managing, and
rendering templates with advanced features like inheritance and component
generation.
"""

import os
import logging
from typing import Dict, Any, Optional, List, Union, Callable
from pathlib import Path
from jinja2 import Environment, PackageLoader, FileSystemLoader, select_autoescape, Template, ChoiceLoader

from .template_context import TemplateContext

logger = logging.getLogger(__name__)


class TemplateManager:
    """
    A class to manage templates for project_tools.
    
    This class is inspired by AppDaemon's templating system and provides
    advanced features like template inheritance, component generation,
    and variable substitution.
    """
    
    def __init__(self, 
                 package_name: str = 'projects_tools', 
                 template_dir: str = 'templates',
                 custom_template_dirs: Optional[List[str]] = None):
        """
        Initialize a new template manager.
        
        Args:
            package_name: Package name for PackageLoader
            template_dir: Template directory within package
            custom_template_dirs: Optional list of custom template directories
        """
        self.package_name = package_name
        self.template_dir = template_dir
        self.custom_template_dirs = custom_template_dirs or []
        
        # Set up loaders
        loaders = []
        
        # Add custom template directories first so they take precedence
        for custom_dir in self.custom_template_dirs:
            if os.path.exists(custom_dir):
                loaders.append(FileSystemLoader(custom_dir))
                
        # Add package loader
        loaders.append(PackageLoader(self.package_name, self.template_dir))
        
        # Create environment with choice loader
        self.env = Environment(
            loader=ChoiceLoader(loaders),
            autoescape=select_autoescape(['html', 'xml']),
            trim_blocks=True,
            lstrip_blocks=True
        )
        
        # Template cache
        self.template_cache = {}
        
        # Register default filters
        self._register_default_filters()
        
    def _register_default_filters(self):
        """Register default filters for templates."""
        # Convert string to snake_case
        self.env.filters['snake_case'] = lambda s: s.lower().replace('-', '_').replace(' ', '_')
        
        # Convert string to kebab-case
        self.env.filters['kebab_case'] = lambda s: s.lower().replace('_', '-').replace(' ', '-')
        
        # Convert string to camelCase
        def to_camel_case(s):
            parts = s.replace('-', '_').replace(' ', '_').split('_')
            return parts[0].lower() + ''.join(p.capitalize() for p in parts[1:])
        self.env.filters['camel_case'] = to_camel_case
        
        # Convert string to PascalCase
        def to_pascal_case(s):
            parts = s.replace('-', '_').replace(' ', '_').split('_')
            return ''.join(p.capitalize() for p in parts)
        self.env.filters['pascal_case'] = to_pascal_case
        
    def add_filter(self, name: str, filter_func: Callable):
        """
        Add a custom filter to the environment.
        
        Args:
            name: Name of the filter
            filter_func: Filter function
        """
        self.env.filters[name] = filter_func
        
    def add_custom_template_dir(self, template_dir: str):
        """
        Add a custom template directory.
        
        Args:
            template_dir: Path to template directory
        """
        if os.path.exists(template_dir):
            self.custom_template_dirs.append(template_dir)
            
            # Update loaders
            loaders = [FileSystemLoader(template_dir)]
            for loader in self.env.loader.loaders:
                loaders.append(loader)
                
            self.env.loader = ChoiceLoader(loaders)
        else:
            logger.warning(f"Template directory not found: {template_dir}")
            
    def get_template(self, template_name: str) -> Template:
        """
        Get a template by name.
        
        Args:
            template_name: Name of the template
            
        Returns:
            Jinja2 Template object
        """
        if template_name not in self.template_cache:
            self.template_cache[template_name] = self.env.get_template(template_name)
            
        return self.template_cache[template_name]
    
    def render_template(self, template_name: str, context: Union[Dict[str, Any], TemplateContext]) -> str:
        """
        Render a template with the given context.
        
        Args:
            template_name: Name of the template
            context: Template context (dict or TemplateContext)
            
        Returns:
            Rendered template string
        """
        template = self.get_template(template_name)
        
        if isinstance(context, TemplateContext):
            # Apply any custom filters from the context
            context.apply_filters_to_env(self.env)
            return template.render(**context.get_merged_context())
        else:
            return template.render(**context)
    
    def render_string(self, template_string: str, context: Union[Dict[str, Any], TemplateContext]) -> str:
        """
        Render a template string with the given context.
        
        Args:
            template_string: Template string to render
            context: Template context (dict or TemplateContext)
            
        Returns:
            Rendered template string
        """
        template = self.env.from_string(template_string)
        
        if isinstance(context, TemplateContext):
            # Apply any custom filters from the context
            context.apply_filters_to_env(self.env)
            return template.render(**context.get_merged_context())
        else:
            return template.render(**context)
    
    def render_to_file(self, template_name: str, output_file: str, 
                       context: Union[Dict[str, Any], TemplateContext],
                       create_dirs: bool = True) -> str:
        """
        Render a template to a file.
        
        Args:
            template_name: Name of the template
            output_file: Path to output file
            context: Template context (dict or TemplateContext)
            create_dirs: Whether to create parent directories
            
        Returns:
            Path to the created file
        """
        # Create parent directories if needed
        if create_dirs:
            os.makedirs(os.path.dirname(os.path.abspath(output_file)), exist_ok=True)
            
        # Render template
        content = self.render_template(template_name, context)
        
        # Write to file
        with open(output_file, 'w') as f:
            f.write(content)
            
        return output_file
    
    def list_templates(self, pattern: Optional[str] = None) -> List[str]:
        """
        List available templates.
        
        Args:
            pattern: Optional glob pattern to filter templates
            
        Returns:
            List of template names
        """
        return self.env.list_templates(filter_func=lambda x: pattern is None or Path(x).match(pattern))
    
    def template_exists(self, template_name: str) -> bool:
        """
        Check if a template exists.
        
        Args:
            template_name: Name of the template
            
        Returns:
            True if template exists, False otherwise
        """
        try:
            self.env.get_template(template_name)
            return True
        except:
            return False
