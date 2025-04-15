"""
Component generator for project_tools.

This module provides a component generator class for generating components
from templates with advanced features like inheritance and variable substitution.
"""

import os
import logging
import json
from typing import Dict, Any, Optional, List, Union, Tuple
from pathlib import Path

from .template_manager import TemplateManager
from .template_context import TemplateContext

logger = logging.getLogger(__name__)


class ComponentGenerator:
    """
    A class to generate components from templates.
    
    This class is inspired by AppDaemon's component generation system and provides
    advanced features like template inheritance, component generation,
    and variable substitution.
    """
    
    def __init__(self, template_manager: TemplateManager):
        """
        Initialize a new component generator.
        
        Args:
            template_manager: Template manager to use
        """
        self.template_manager = template_manager
        self.component_registry = {}
        self.base_components = {}
        
    def register_component(self, component_name: str, 
                          template_files: Dict[str, str],
                          base_component: Optional[str] = None,
                          description: Optional[str] = None):
        """
        Register a component.
        
        Args:
            component_name: Name of the component
            template_files: Dictionary of template files (output_path -> template_name)
            base_component: Optional base component to inherit from
            description: Optional description of the component
        """
        self.component_registry[component_name] = {
            'template_files': template_files,
            'base_component': base_component,
            'description': description or f"Component: {component_name}"
        }
        
    def register_base_component(self, component_name: str,
                               template_files: Dict[str, str],
                               description: Optional[str] = None,
                               required_vars: Optional[List[str]] = None):
        """
        Register a base component.
        
        Args:
            component_name: Name of the component
            template_files: Dictionary of template files (output_path -> template_name)
            description: Optional description of the component
            required_vars: Optional list of required variables
        """
        self.base_components[component_name] = {
            'template_files': template_files,
            'description': description or f"Base Component: {component_name}",
            'required_vars': required_vars or []
        }
        
    def load_component_registry(self, registry_file: str):
        """
        Load component registry from a JSON file.
        
        Args:
            registry_file: Path to registry file
        """
        if os.path.exists(registry_file):
            with open(registry_file, 'r') as f:
                registry = json.load(f)
                
                if 'components' in registry:
                    for name, config in registry['components'].items():
                        self.register_component(
                            name,
                            config.get('template_files', {}),
                            config.get('base_component'),
                            config.get('description')
                        )
                        
                if 'base_components' in registry:
                    for name, config in registry['base_components'].items():
                        self.register_base_component(
                            name,
                            config.get('template_files', {}),
                            config.get('description'),
                            config.get('required_vars')
                        )
                        
    def save_component_registry(self, registry_file: str):
        """
        Save component registry to a JSON file.
        
        Args:
            registry_file: Path to registry file
        """
        registry = {
            'components': self.component_registry,
            'base_components': self.base_components
        }
        
        with open(registry_file, 'w') as f:
            json.dump(registry, f, indent=2)
            
    def list_components(self) -> List[Dict[str, Any]]:
        """
        List all registered components.
        
        Returns:
            List of component information
        """
        result = []
        
        for name, config in self.component_registry.items():
            result.append({
                'name': name,
                'description': config.get('description', ''),
                'base_component': config.get('base_component'),
                'template_files': list(config.get('template_files', {}).keys())
            })
            
        return result
    
    def list_base_components(self) -> List[Dict[str, Any]]:
        """
        List all registered base components.
        
        Returns:
            List of base component information
        """
        result = []
        
        for name, config in self.base_components.items():
            result.append({
                'name': name,
                'description': config.get('description', ''),
                'required_vars': config.get('required_vars', []),
                'template_files': list(config.get('template_files', {}).keys())
            })
            
        return result
    
    def get_component_info(self, component_name: str) -> Optional[Dict[str, Any]]:
        """
        Get information about a component.
        
        Args:
            component_name: Name of the component
            
        Returns:
            Component information or None if not found
        """
        if component_name in self.component_registry:
            config = self.component_registry[component_name]
            return {
                'name': component_name,
                'description': config.get('description', ''),
                'base_component': config.get('base_component'),
                'template_files': list(config.get('template_files', {}).keys())
            }
        elif component_name in self.base_components:
            config = self.base_components[component_name]
            return {
                'name': component_name,
                'description': config.get('description', ''),
                'required_vars': config.get('required_vars', []),
                'template_files': list(config.get('template_files', {}).keys()),
                'is_base': True
            }
        else:
            return None
    
    def _get_merged_template_files(self, component_name: str) -> Dict[str, str]:
        """
        Get merged template files for a component, including base components.
        
        Args:
            component_name: Name of the component
            
        Returns:
            Dictionary of template files (output_path -> template_name)
        """
        if component_name in self.base_components:
            return self.base_components[component_name]['template_files']
            
        if component_name not in self.component_registry:
            raise ValueError(f"Component not found: {component_name}")
            
        config = self.component_registry[component_name]
        result = {}
        
        # Include base component templates if specified
        if config.get('base_component') and config['base_component'] in self.base_components:
            base_templates = self.base_components[config['base_component']]['template_files']
            result.update(base_templates)
            
        # Override with component's own templates
        result.update(config['template_files'])
        
        return result
    
    def _validate_context(self, component_name: str, context: Union[Dict[str, Any], TemplateContext]) -> List[str]:
        """
        Validate context for a component.
        
        Args:
            component_name: Name of the component
            context: Template context
            
        Returns:
            List of missing required variables
        """
        # Get required variables from base component
        required_vars = []
        
        if component_name in self.component_registry:
            config = self.component_registry[component_name]
            if config.get('base_component') and config['base_component'] in self.base_components:
                required_vars = self.base_components[config['base_component']].get('required_vars', [])
        elif component_name in self.base_components:
            required_vars = self.base_components[component_name].get('required_vars', [])
        else:
            raise ValueError(f"Component not found: {component_name}")
            
        # Check if all required variables are present
        missing_vars = []
        
        if isinstance(context, TemplateContext):
            context_dict = context.get_merged_context()
        else:
            context_dict = context
            
        for var in required_vars:
            if var not in context_dict:
                missing_vars.append(var)
                
        return missing_vars
    
    def generate_component(self, component_name: str, 
                          output_dir: str,
                          context: Union[Dict[str, Any], TemplateContext],
                          validate: bool = True) -> List[str]:
        """
        Generate a component.
        
        Args:
            component_name: Name of the component
            output_dir: Output directory
            context: Template context
            validate: Whether to validate required variables
            
        Returns:
            List of generated files
        """
        # Validate context if requested
        if validate:
            missing_vars = self._validate_context(component_name, context)
            if missing_vars:
                raise ValueError(f"Missing required variables for component {component_name}: {', '.join(missing_vars)}")
                
        # Get merged template files
        template_files = self._get_merged_template_files(component_name)
        
        # Generate files
        generated_files = []
        
        for output_path, template_name in template_files.items():
            # Resolve output path with context
            if isinstance(context, TemplateContext):
                resolved_path = self.template_manager.render_string(output_path, context)
            else:
                resolved_path = self.template_manager.render_string(output_path, context)
                
            # Create full output path
            full_output_path = os.path.join(output_dir, resolved_path)
            
            # Render template to file
            self.template_manager.render_to_file(template_name, full_output_path, context)
            
            generated_files.append(full_output_path)
            
        return generated_files
    
    def generate_component_preview(self, component_name: str,
                                  context: Union[Dict[str, Any], TemplateContext],
                                  validate: bool = True) -> Dict[str, str]:
        """
        Generate a preview of a component without writing to files.
        
        Args:
            component_name: Name of the component
            context: Template context
            validate: Whether to validate required variables
            
        Returns:
            Dictionary of output paths to rendered content
        """
        # Validate context if requested
        if validate:
            missing_vars = self._validate_context(component_name, context)
            if missing_vars:
                raise ValueError(f"Missing required variables for component {component_name}: {', '.join(missing_vars)}")
                
        # Get merged template files
        template_files = self._get_merged_template_files(component_name)
        
        # Generate previews
        previews = {}
        
        for output_path, template_name in template_files.items():
            # Resolve output path with context
            if isinstance(context, TemplateContext):
                resolved_path = self.template_manager.render_string(output_path, context)
            else:
                resolved_path = self.template_manager.render_string(output_path, context)
                
            # Render template
            content = self.template_manager.render_template(template_name, context)
            
            previews[resolved_path] = content
            
        return previews
