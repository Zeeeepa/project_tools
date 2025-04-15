"""
Layout generator for project_tools.

This module provides a layout generator class for generating layouts from
templates with advanced features like inheritance and variable substitution.
"""

import os
import logging
import json
from typing import Dict, Any, Optional, List, Union, Tuple
from pathlib import Path

from .template_manager import TemplateManager
from .template_context import TemplateContext
from .template_registry import TemplateRegistry
from .pattern_generator import PatternGenerator

logger = logging.getLogger(__name__)


class LayoutGenerator:
    """
    A class to generate layouts from templates.
    
    This class provides functionality for generating layouts from templates
    with advanced features like inheritance and variable substitution.
    """
    
    def __init__(self, 
                template_manager: TemplateManager,
                template_registry: TemplateRegistry,
                pattern_generator: PatternGenerator):
        """
        Initialize a new layout generator.
        
        Args:
            template_manager: Template manager to use
            template_registry: Template registry to use
            pattern_generator: Pattern generator to use
        """
        self.template_manager = template_manager
        self.template_registry = template_registry
        self.pattern_generator = pattern_generator
        self.layouts = {}
        
    def register_layout(self,
                       layout_id: str,
                       components: List[Dict[str, Any]],
                       description: Optional[str] = None):
        """
        Register a layout.
        
        Args:
            layout_id: Unique identifier for the layout
            components: List of component definitions
            description: Optional description of the layout
        """
        self.layouts[layout_id] = {
            'components': components,
            'description': description or f"Layout: {layout_id}"
        }
        
    def load_layouts_from_file(self, layout_file: str):
        """
        Load layouts from a JSON file.
        
        Args:
            layout_file: Path to layout file
        """
        if not os.path.exists(layout_file):
            logger.warning(f"Layout file not found: {layout_file}")
            return
        
        with open(layout_file, 'r') as f:
            layouts = json.load(f)
            
        for layout_id, layout_info in layouts.items():
            self.register_layout(
                layout_id,
                layout_info.get('components', []),
                layout_info.get('description')
            )
            
    def save_layouts_to_file(self, layout_file: str):
        """
        Save layouts to a JSON file.
        
        Args:
            layout_file: Path to layout file
        """
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(os.path.abspath(layout_file)), exist_ok=True)
        
        with open(layout_file, 'w') as f:
            json.dump(self.layouts, f, indent=2)
            
    def list_layouts(self) -> List[Dict[str, Any]]:
        """
        List all registered layouts.
        
        Returns:
            List of layout information
        """
        return [
            {
                'id': layout_id,
                'description': info['description'],
                'component_count': len(info['components'])
            }
            for layout_id, info in self.layouts.items()
        ]
        
    def get_layout_info(self, layout_id: str) -> Optional[Dict[str, Any]]:
        """
        Get information about a layout.
        
        Args:
            layout_id: ID of the layout
            
        Returns:
            Layout information or None if not found
        """
        if layout_id not in self.layouts:
            return None
            
        layout_info = self.layouts[layout_id]
        return {
            'id': layout_id,
            'description': layout_info['description'],
            'components': layout_info['components']
        }
        
    def generate_layout(self,
                       layout_id: str,
                       context: Union[Dict[str, Any], TemplateContext],
                       output_dir: str,
                       validate: bool = True) -> List[str]:
        """
        Generate a layout.
        
        Args:
            layout_id: ID of the layout to generate
            context: Template context
            output_dir: Output directory
            validate: Whether to validate required variables
            
        Returns:
            List of generated files
        """
        if layout_id not in self.layouts:
            raise ValueError(f"Layout not found: {layout_id}")
            
        layout_info = self.layouts[layout_id]
        generated_files = []
        
        # Convert context to TemplateContext if needed
        if isinstance(context, dict):
            context = TemplateContext(context)
            
        # Generate each component
        for component in layout_info['components']:
            component_type = component.get('type')
            component_id = component.get('id')
            output_path = component.get('output_path')
            
            # Resolve output path with context
            if output_path:
                output_path = self.template_manager.render_string(output_path, context)
                full_output_path = os.path.join(output_dir, output_path)
            else:
                full_output_path = None
                
            # Generate content based on component type
            if component_type == 'template':
                if not component_id:
                    raise ValueError(f"Template component missing 'id' in layout {layout_id}")
                    
                content = self.pattern_generator.generate_from_template(
                    component_id,
                    context,
                    full_output_path
                )
                
                if full_output_path:
                    generated_files.append(full_output_path)
                    
            elif component_type == 'pattern':
                if not component_id:
                    raise ValueError(f"Pattern component missing 'id' in layout {layout_id}")
                    
                content = self.pattern_generator.generate_from_pattern(
                    component_id,
                    context,
                    full_output_path
                )
                
                if full_output_path:
                    generated_files.append(full_output_path)
                    
            elif component_type == 'algorithm':
                if not component_id:
                    raise ValueError(f"Algorithm component missing 'id' in layout {layout_id}")
                    
                # Extract parameters from context
                algorithm_info = self.template_registry.get_algorithm(component_id)
                if not algorithm_info:
                    raise ValueError(f"Algorithm not found: {component_id}")
                    
                context_dict = context.get_merged_context()
                parameters = {
                    param: context_dict.get(param)
                    for param in algorithm_info['parameters']
                    if param in context_dict
                }
                
                content = self.pattern_generator.generate_from_algorithm(
                    component_id,
                    parameters,
                    full_output_path
                )
                
                if full_output_path:
                    generated_files.append(full_output_path)
                    
            elif component_type == 'metadata':
                if not component.get('key') or not component.get('value'):
                    raise ValueError(f"Metadata component missing 'key' or 'value' in layout {layout_id}")
                    
                # Find and generate content by metadata
                metadata_key = component['key']
                metadata_value = component['value']
                
                # Resolve metadata value with context if it's a string
                if isinstance(metadata_value, str) and '{{' in metadata_value:
                    metadata_value = self.template_manager.render_string(metadata_value, context)
                    
                # Create output directory for this component if needed
                component_output_dir = None
                if full_output_path:
                    component_output_dir = os.path.dirname(full_output_path)
                    os.makedirs(component_output_dir, exist_ok=True)
                    
                # Generate content
                generated = self.pattern_generator.find_and_generate(
                    metadata_key,
                    metadata_value,
                    context,
                    component_output_dir
                )
                
                # Add generated files to the list
                if component_output_dir:
                    for item_id, content in generated.items():
                        if component_type == 'template':
                            template_info = self.template_registry.get_template(item_id)
                            if template_info:
                                file_path = os.path.join(component_output_dir, os.path.basename(template_info['path']))
                                generated_files.append(file_path)
                        else:
                            file_path = os.path.join(component_output_dir, f"{item_id}.txt")
                            generated_files.append(file_path)
            else:
                logger.warning(f"Unknown component type: {component_type} in layout {layout_id}")
                
        return generated_files
        
    def generate_layout_preview(self,
                              layout_id: str,
                              context: Union[Dict[str, Any], TemplateContext],
                              validate: bool = True) -> Dict[str, str]:
        """
        Generate a preview of a layout without writing to files.
        
        Args:
            layout_id: ID of the layout to generate
            context: Template context
            validate: Whether to validate required variables
            
        Returns:
            Dictionary of output paths to rendered content
        """
        if layout_id not in self.layouts:
            raise ValueError(f"Layout not found: {layout_id}")
            
        layout_info = self.layouts[layout_id]
        previews = {}
        
        # Convert context to TemplateContext if needed
        if isinstance(context, dict):
            context = TemplateContext(context)
            
        # Generate each component
        for component in layout_info['components']:
            component_type = component.get('type')
            component_id = component.get('id')
            output_path = component.get('output_path')
            
            # Resolve output path with context
            if output_path:
                output_path = self.template_manager.render_string(output_path, context)
            else:
                output_path = f"{component_type}_{component_id}"
                
            # Generate content based on component type
            if component_type == 'template':
                if not component_id:
                    raise ValueError(f"Template component missing 'id' in layout {layout_id}")
                    
                content = self.pattern_generator.generate_from_template(
                    component_id,
                    context
                )
                
                previews[output_path] = content
                    
            elif component_type == 'pattern':
                if not component_id:
                    raise ValueError(f"Pattern component missing 'id' in layout {layout_id}")
                    
                content = self.pattern_generator.generate_from_pattern(
                    component_id,
                    context
                )
                
                previews[output_path] = content
                    
            elif component_type == 'algorithm':
                if not component_id:
                    raise ValueError(f"Algorithm component missing 'id' in layout {layout_id}")
                    
                # Extract parameters from context
                algorithm_info = self.template_registry.get_algorithm(component_id)
                if not algorithm_info:
                    raise ValueError(f"Algorithm not found: {component_id}")
                    
                context_dict = context.get_merged_context()
                parameters = {
                    param: context_dict.get(param)
                    for param in algorithm_info['parameters']
                    if param in context_dict
                }
                
                content = self.pattern_generator.generate_from_algorithm(
                    component_id,
                    parameters
                )
                
                previews[output_path] = content
                    
            elif component_type == 'metadata':
                if not component.get('key') or not component.get('value'):
                    raise ValueError(f"Metadata component missing 'key' or 'value' in layout {layout_id}")
                    
                # Find and generate content by metadata
                metadata_key = component['key']
                metadata_value = component['value']
                
                # Resolve metadata value with context if it's a string
                if isinstance(metadata_value, str) and '{{' in metadata_value:
                    metadata_value = self.template_manager.render_string(metadata_value, context)
                    
                # Generate content
                generated = self.pattern_generator.find_and_generate(
                    metadata_key,
                    metadata_value,
                    context
                )
                
                # Add generated content to previews
                for item_id, content in generated.items():
                    previews[f"{output_path}/{item_id}"] = content
            else:
                logger.warning(f"Unknown component type: {component_type} in layout {layout_id}")
                
        return previews
