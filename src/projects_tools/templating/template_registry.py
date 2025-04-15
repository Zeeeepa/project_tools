"""
Template registry for project_tools.

This module provides a registry system for managing templates, patterns, and
algorithmic generation patterns for highly accurate templated content.
"""

import os
import json
import logging
from typing import Dict, Any, Optional, List, Union, Callable
from pathlib import Path

logger = logging.getLogger(__name__)


class TemplateRegistry:
    """
    A registry for managing templates, patterns, and algorithmic generation patterns.
    
    This class provides a centralized system for registering, discovering, and
    managing templates and generation patterns for creating highly accurate
    templated content.
    """
    
    def __init__(self, registry_file: Optional[str] = None):
        """
        Initialize a new template registry.
        
        Args:
            registry_file: Optional path to a registry file to load
        """
        self.templates = {}
        self.patterns = {}
        self.algorithms = {}
        self.metadata = {}
        
        if registry_file and os.path.exists(registry_file):
            self.load_from_file(registry_file)
    
    def register_template(self, 
                         template_id: str, 
                         template_path: str,
                         metadata: Optional[Dict[str, Any]] = None):
        """
        Register a template.
        
        Args:
            template_id: Unique identifier for the template
            template_path: Path to the template file
            metadata: Optional metadata for the template
        """
        self.templates[template_id] = {
            'path': template_path,
            'metadata': metadata or {}
        }
        
        # Update metadata index
        for key, value in (metadata or {}).items():
            if key not in self.metadata:
                self.metadata[key] = {}
            
            if value not in self.metadata[key]:
                self.metadata[key][value] = []
                
            if template_id not in self.metadata[key][value]:
                self.metadata[key][value].append(template_id)
    
    def register_pattern(self,
                        pattern_id: str,
                        pattern_template: str,
                        variables: List[str],
                        metadata: Optional[Dict[str, Any]] = None):
        """
        Register a pattern.
        
        Args:
            pattern_id: Unique identifier for the pattern
            pattern_template: Template string for the pattern
            variables: List of variables used in the pattern
            metadata: Optional metadata for the pattern
        """
        self.patterns[pattern_id] = {
            'template': pattern_template,
            'variables': variables,
            'metadata': metadata or {}
        }
        
        # Update metadata index
        for key, value in (metadata or {}).items():
            if key not in self.metadata:
                self.metadata[key] = {}
            
            if value not in self.metadata[key]:
                self.metadata[key][value] = []
                
            if pattern_id not in self.metadata[key][value]:
                self.metadata[key][value].append(pattern_id)
    
    def register_algorithm(self,
                          algorithm_id: str,
                          generator_func: Callable,
                          parameters: List[str],
                          metadata: Optional[Dict[str, Any]] = None):
        """
        Register an algorithmic generation pattern.
        
        Args:
            algorithm_id: Unique identifier for the algorithm
            generator_func: Function that generates content
            parameters: List of parameters for the generator function
            metadata: Optional metadata for the algorithm
        """
        self.algorithms[algorithm_id] = {
            'generator': generator_func,
            'parameters': parameters,
            'metadata': metadata or {}
        }
        
        # Update metadata index
        for key, value in (metadata or {}).items():
            if key not in self.metadata:
                self.metadata[key] = {}
            
            if value not in self.metadata[key]:
                self.metadata[key][value] = []
                
            if algorithm_id not in self.metadata[key][value]:
                self.metadata[key][value].append(algorithm_id)
    
    def get_template(self, template_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a template by ID.
        
        Args:
            template_id: ID of the template to get
            
        Returns:
            Template information or None if not found
        """
        return self.templates.get(template_id)
    
    def get_pattern(self, pattern_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a pattern by ID.
        
        Args:
            pattern_id: ID of the pattern to get
            
        Returns:
            Pattern information or None if not found
        """
        return self.patterns.get(pattern_id)
    
    def get_algorithm(self, algorithm_id: str) -> Optional[Dict[str, Any]]:
        """
        Get an algorithm by ID.
        
        Args:
            algorithm_id: ID of the algorithm to get
            
        Returns:
            Algorithm information or None if not found
        """
        return self.algorithms.get(algorithm_id)
    
    def find_by_metadata(self, key: str, value: Any) -> Dict[str, List[str]]:
        """
        Find templates, patterns, and algorithms by metadata.
        
        Args:
            key: Metadata key to search for
            value: Metadata value to match
            
        Returns:
            Dictionary of template, pattern, and algorithm IDs that match
        """
        result = {
            'templates': [],
            'patterns': [],
            'algorithms': []
        }
        
        if key in self.metadata and value in self.metadata[key]:
            for item_id in self.metadata[key][value]:
                if item_id in self.templates:
                    result['templates'].append(item_id)
                elif item_id in self.patterns:
                    result['patterns'].append(item_id)
                elif item_id in self.algorithms:
                    result['algorithms'].append(item_id)
        
        return result
    
    def list_templates(self) -> List[Dict[str, Any]]:
        """
        List all registered templates.
        
        Returns:
            List of template information
        """
        return [
            {
                'id': template_id,
                'path': info['path'],
                'metadata': info['metadata']
            }
            for template_id, info in self.templates.items()
        ]
    
    def list_patterns(self) -> List[Dict[str, Any]]:
        """
        List all registered patterns.
        
        Returns:
            List of pattern information
        """
        return [
            {
                'id': pattern_id,
                'template': info['template'],
                'variables': info['variables'],
                'metadata': info['metadata']
            }
            for pattern_id, info in self.patterns.items()
        ]
    
    def list_algorithms(self) -> List[Dict[str, Any]]:
        """
        List all registered algorithms.
        
        Returns:
            List of algorithm information
        """
        return [
            {
                'id': algorithm_id,
                'parameters': info['parameters'],
                'metadata': info['metadata']
            }
            for algorithm_id, info in self.algorithms.items()
        ]
    
    def save_to_file(self, registry_file: str):
        """
        Save the registry to a file.
        
        Args:
            registry_file: Path to save the registry to
        """
        # Create a serializable version of the registry
        registry_data = {
            'templates': {},
            'patterns': {},
            'algorithms': {}
        }
        
        # Save templates
        for template_id, info in self.templates.items():
            registry_data['templates'][template_id] = {
                'path': info['path'],
                'metadata': info['metadata']
            }
        
        # Save patterns
        for pattern_id, info in self.patterns.items():
            registry_data['patterns'][pattern_id] = {
                'template': info['template'],
                'variables': info['variables'],
                'metadata': info['metadata']
            }
        
        # Save algorithms (just metadata and parameters, not the function)
        for algorithm_id, info in self.algorithms.items():
            registry_data['algorithms'][algorithm_id] = {
                'parameters': info['parameters'],
                'metadata': info['metadata']
            }
        
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(os.path.abspath(registry_file)), exist_ok=True)
        
        # Write to file
        with open(registry_file, 'w') as f:
            json.dump(registry_data, f, indent=2)
    
    def load_from_file(self, registry_file: str):
        """
        Load the registry from a file.
        
        Args:
            registry_file: Path to load the registry from
        """
        if not os.path.exists(registry_file):
            logger.warning(f"Registry file not found: {registry_file}")
            return
        
        with open(registry_file, 'r') as f:
            registry_data = json.load(f)
        
        # Load templates
        for template_id, info in registry_data.get('templates', {}).items():
            self.templates[template_id] = {
                'path': info['path'],
                'metadata': info.get('metadata', {})
            }
        
        # Load patterns
        for pattern_id, info in registry_data.get('patterns', {}).items():
            self.patterns[pattern_id] = {
                'template': info['template'],
                'variables': info.get('variables', []),
                'metadata': info.get('metadata', {})
            }
        
        # Load algorithms (note: functions need to be registered separately)
        for algorithm_id, info in registry_data.get('algorithms', {}).items():
            self.algorithms[algorithm_id] = {
                'generator': None,  # Function needs to be registered separately
                'parameters': info.get('parameters', []),
                'metadata': info.get('metadata', {})
            }
        
        # Rebuild metadata index
        self.metadata = {}
        
        # Index templates
        for template_id, info in self.templates.items():
            for key, value in info['metadata'].items():
                if key not in self.metadata:
                    self.metadata[key] = {}
                
                if value not in self.metadata[key]:
                    self.metadata[key][value] = []
                    
                if template_id not in self.metadata[key][value]:
                    self.metadata[key][value].append(template_id)
        
        # Index patterns
        for pattern_id, info in self.patterns.items():
            for key, value in info['metadata'].items():
                if key not in self.metadata:
                    self.metadata[key] = {}
                
                if value not in self.metadata[key]:
                    self.metadata[key][value] = []
                    
                if pattern_id not in self.metadata[key][value]:
                    self.metadata[key][value].append(pattern_id)
        
        # Index algorithms
        for algorithm_id, info in self.algorithms.items():
            for key, value in info['metadata'].items():
                if key not in self.metadata:
                    self.metadata[key] = {}
                
                if value not in self.metadata[key]:
                    self.metadata[key][value] = []
                    
                if algorithm_id not in self.metadata[key][value]:
                    self.metadata[key][value].append(algorithm_id)
