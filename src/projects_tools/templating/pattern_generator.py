"""
Pattern generator for project_tools.

This module provides a pattern generator class for generating content from
patterns with advanced features like variable substitution and algorithmic
generation.
"""

import os
import logging
import re
from typing import Dict, Any, Optional, List, Union, Callable, Tuple
from pathlib import Path

from .template_registry import TemplateRegistry
from .template_manager import TemplateManager
from .template_context import TemplateContext

logger = logging.getLogger(__name__)


class PatternGenerator:
    """
    A class to generate content from patterns.
    
    This class provides functionality for generating content from patterns
    with advanced features like variable substitution and algorithmic
    generation.
    """
    
    def __init__(self, 
                template_manager: TemplateManager,
                template_registry: TemplateRegistry):
        """
        Initialize a new pattern generator.
        
        Args:
            template_manager: Template manager to use
            template_registry: Template registry to use
        """
        self.template_manager = template_manager
        self.template_registry = template_registry
        
    def generate_from_pattern(self, 
                             pattern_id: str,
                             context: Union[Dict[str, Any], TemplateContext],
                             output_path: Optional[str] = None) -> str:
        """
        Generate content from a pattern.
        
        Args:
            pattern_id: ID of the pattern to use
            context: Template context
            output_path: Optional path to write the output to
            
        Returns:
            Generated content
        """
        # Get pattern
        pattern_info = self.template_registry.get_pattern(pattern_id)
        if not pattern_info:
            raise ValueError(f"Pattern not found: {pattern_id}")
        
        # Validate context
        if isinstance(context, dict):
            context_dict = context
            context = TemplateContext(context)
        else:
            context_dict = context.get_merged_context()
        
        # Check for required variables
        missing_vars = []
        for var in pattern_info['variables']:
            if var not in context_dict:
                missing_vars.append(var)
        
        if missing_vars:
            raise ValueError(f"Missing required variables for pattern {pattern_id}: {', '.join(missing_vars)}")
        
        # Render pattern
        content = self.template_manager.render_string(pattern_info['template'], context)
        
        # Write to file if requested
        if output_path:
            os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
            with open(output_path, 'w') as f:
                f.write(content)
        
        return content
    
    def generate_from_algorithm(self,
                               algorithm_id: str,
                               parameters: Dict[str, Any],
                               output_path: Optional[str] = None) -> str:
        """
        Generate content from an algorithm.
        
        Args:
            algorithm_id: ID of the algorithm to use
            parameters: Parameters for the algorithm
            output_path: Optional path to write the output to
            
        Returns:
            Generated content
        """
        # Get algorithm
        algorithm_info = self.template_registry.get_algorithm(algorithm_id)
        if not algorithm_info:
            raise ValueError(f"Algorithm not found: {algorithm_id}")
        
        # Check for required parameters
        missing_params = []
        for param in algorithm_info['parameters']:
            if param not in parameters:
                missing_params.append(param)
        
        if missing_params:
            raise ValueError(f"Missing required parameters for algorithm {algorithm_id}: {', '.join(missing_params)}")
        
        # Generate content
        generator_func = algorithm_info['generator']
        if not generator_func:
            raise ValueError(f"Generator function not found for algorithm {algorithm_id}")
        
        content = generator_func(**parameters)
        
        # Write to file if requested
        if output_path:
            os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
            with open(output_path, 'w') as f:
                f.write(content)
        
        return content
    
    def generate_from_template(self,
                              template_id: str,
                              context: Union[Dict[str, Any], TemplateContext],
                              output_path: Optional[str] = None) -> str:
        """
        Generate content from a template.
        
        Args:
            template_id: ID of the template to use
            context: Template context
            output_path: Optional path to write the output to
            
        Returns:
            Generated content
        """
        # Get template
        template_info = self.template_registry.get_template(template_id)
        if not template_info:
            raise ValueError(f"Template not found: {template_id}")
        
        # Render template
        content = self.template_manager.render_template(template_info['path'], context)
        
        # Write to file if requested
        if output_path:
            os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
            with open(output_path, 'w') as f:
                f.write(content)
        
        return content
    
    def find_and_generate(self,
                         metadata_key: str,
                         metadata_value: Any,
                         context: Union[Dict[str, Any], TemplateContext],
                         output_dir: Optional[str] = None) -> Dict[str, str]:
        """
        Find templates, patterns, and algorithms by metadata and generate content.
        
        Args:
            metadata_key: Metadata key to search for
            metadata_value: Metadata value to match
            context: Template context
            output_dir: Optional directory to write output files to
            
        Returns:
            Dictionary of generated content (ID -> content)
        """
        # Find items by metadata
        items = self.template_registry.find_by_metadata(metadata_key, metadata_value)
        
        # Generate content
        result = {}
        
        # Generate from templates
        for template_id in items['templates']:
            template_info = self.template_registry.get_template(template_id)
            output_path = None
            
            if output_dir:
                output_path = os.path.join(output_dir, os.path.basename(template_info['path']))
            
            content = self.generate_from_template(template_id, context, output_path)
            result[template_id] = content
        
        # Generate from patterns
        for pattern_id in items['patterns']:
            output_path = None
            
            if output_dir:
                output_path = os.path.join(output_dir, f"{pattern_id}.txt")
            
            content = self.generate_from_pattern(pattern_id, context, output_path)
            result[pattern_id] = content
        
        # Generate from algorithms
        for algorithm_id in items['algorithms']:
            algorithm_info = self.template_registry.get_algorithm(algorithm_id)
            
            # Extract parameters from context
            if isinstance(context, dict):
                parameters = {
                    param: context.get(param)
                    for param in algorithm_info['parameters']
                    if param in context
                }
            else:
                context_dict = context.get_merged_context()
                parameters = {
                    param: context_dict.get(param)
                    for param in algorithm_info['parameters']
                    if param in context_dict
                }
            
            output_path = None
            
            if output_dir:
                output_path = os.path.join(output_dir, f"{algorithm_id}.txt")
            
            content = self.generate_from_algorithm(algorithm_id, parameters, output_path)
            result[algorithm_id] = content
        
        return result
