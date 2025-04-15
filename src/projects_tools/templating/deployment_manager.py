"""
Deployment template manager for project_tools.

This module provides a deployment manager class for generating deployment
configurations with advanced features like environment-specific settings,
service definitions, and container orchestration.
"""

import os
import logging
import json
import yaml
from typing import Dict, Any, Optional, List, Union, Tuple
from pathlib import Path

from .template_manager import TemplateManager
from .template_context import TemplateContext

logger = logging.getLogger(__name__)


class DeploymentManager:
    """
    A class to manage deployment configurations for projects.
    
    This class is inspired by AppDaemon's component generation system and provides
    advanced features for generating deployment configurations for different
    environments and deployment targets.
    """
    
    def __init__(self, template_manager: TemplateManager):
        """
        Initialize a new deployment manager.
        
        Args:
            template_manager: Template manager to use
        """
        self.template_manager = template_manager
        self.deployment_registry = {}
        self.environment_registry = {}
        
    def register_deployment_type(self, deployment_type: str, 
                               template_files: Dict[str, str],
                               description: Optional[str] = None,
                               required_vars: Optional[List[str]] = None):
        """
        Register a deployment type.
        
        Args:
            deployment_type: Type of deployment (e.g., docker, kubernetes, serverless)
            template_files: Dictionary of template files (output_path -> template_name)
            description: Optional description of the deployment type
            required_vars: Optional list of required variables
        """
        self.deployment_registry[deployment_type] = {
            'template_files': template_files,
            'description': description or f"Deployment type: {deployment_type}",
            'required_vars': required_vars or []
        }
        
    def register_environment(self, environment_name: str,
                           variables: Dict[str, Any],
                           description: Optional[str] = None):
        """
        Register an environment with specific variables.
        
        Args:
            environment_name: Name of the environment (e.g., development, staging, production)
            variables: Dictionary of environment-specific variables
            description: Optional description of the environment
        """
        self.environment_registry[environment_name] = {
            'variables': variables,
            'description': description or f"Environment: {environment_name}"
        }
        
    def load_deployment_registry(self, registry_file: str):
        """
        Load deployment registry from a JSON file.
        
        Args:
            registry_file: Path to registry file
        """
        if os.path.exists(registry_file):
            with open(registry_file, 'r') as f:
                registry = json.load(f)
                
                if 'deployment_types' in registry:
                    for name, config in registry['deployment_types'].items():
                        self.register_deployment_type(
                            name,
                            config.get('template_files', {}),
                            config.get('description'),
                            config.get('required_vars')
                        )
                        
                if 'environments' in registry:
                    for name, config in registry['environments'].items():
                        self.register_environment(
                            name,
                            config.get('variables', {}),
                            config.get('description')
                        )
                        
    def save_deployment_registry(self, registry_file: str):
        """
        Save deployment registry to a JSON file.
        
        Args:
            registry_file: Path to registry file
        """
        registry = {
            'deployment_types': self.deployment_registry,
            'environments': self.environment_registry
        }
        
        with open(registry_file, 'w') as f:
            json.dump(registry, f, indent=2)
            
    def list_deployment_types(self) -> List[Dict[str, Any]]:
        """
        List all registered deployment types.
        
        Returns:
            List of deployment type information
        """
        result = []
        
        for name, config in self.deployment_registry.items():
            result.append({
                'name': name,
                'description': config.get('description', ''),
                'required_vars': config.get('required_vars', []),
                'template_files': list(config.get('template_files', {}).keys())
            })
            
        return result
    
    def list_environments(self) -> List[Dict[str, Any]]:
        """
        List all registered environments.
        
        Returns:
            List of environment information
        """
        result = []
        
        for name, config in self.environment_registry.items():
            result.append({
                'name': name,
                'description': config.get('description', ''),
                'variables': config.get('variables', {})
            })
            
        return result
    
    def get_deployment_type_info(self, deployment_type: str) -> Optional[Dict[str, Any]]:
        """
        Get information about a deployment type.
        
        Args:
            deployment_type: Name of the deployment type
            
        Returns:
            Dictionary with deployment type information or None if not found
        """
        if deployment_type in self.deployment_registry:
            config = self.deployment_registry[deployment_type]
            return {
                'name': deployment_type,
                'description': config.get('description', ''),
                'required_vars': config.get('required_vars', []),
                'template_files': config.get('template_files', {})
            }
        return None
    
    def get_environment_info(self, environment_name: str) -> Optional[Dict[str, Any]]:
        """
        Get information about an environment.
        
        Args:
            environment_name: Name of the environment
            
        Returns:
            Dictionary with environment information or None if not found
        """
        if environment_name in self.environment_registry:
            config = self.environment_registry[environment_name]
            return {
                'name': environment_name,
                'description': config.get('description', ''),
                'variables': config.get('variables', {})
            }
        return None
    
    def validate_deployment_variables(self, deployment_type: str, 
                                    context: TemplateContext) -> Tuple[bool, List[str]]:
        """
        Validate that all required variables for a deployment type are present.
        
        Args:
            deployment_type: Name of the deployment type
            context: Template context with variables
            
        Returns:
            Tuple of (is_valid, missing_variables)
        """
        if deployment_type not in self.deployment_registry:
            return False, [f"Deployment type '{deployment_type}' not found"]
        
        required_vars = self.deployment_registry[deployment_type].get('required_vars', [])
        missing_vars = []
        
        for var in required_vars:
            if var not in context:
                missing_vars.append(var)
                
        return len(missing_vars) == 0, missing_vars
    
    def generate_deployment_preview(self, deployment_type: str, 
                                  environment_name: Optional[str],
                                  context: TemplateContext) -> Dict[str, str]:
        """
        Generate a preview of deployment files without writing them to disk.
        
        Args:
            deployment_type: Type of deployment to generate
            environment_name: Optional environment name to use
            context: Template context with variables
            
        Returns:
            Dictionary of file paths to file contents
        """
        if deployment_type not in self.deployment_registry:
            raise ValueError(f"Deployment type '{deployment_type}' not found")
        
        # Validate required variables
        is_valid, missing_vars = self.validate_deployment_variables(deployment_type, context)
        if not is_valid:
            raise ValueError(f"Missing required variables: {', '.join(missing_vars)}")
        
        # Add environment variables if specified
        if environment_name is not None:
            if environment_name not in self.environment_registry:
                raise ValueError(f"Environment '{environment_name}' not found")
            
            # Create a new context with environment variables
            env_context = TemplateContext(self.environment_registry[environment_name].get('variables', {}))
            
            # Create a new context that inherits from both
            merged_context = TemplateContext(context.context)
            merged_context.inherit_from(env_context)
            context = merged_context
        
        # Get template files
        template_files = self.deployment_registry[deployment_type].get('template_files', {})
        
        # Generate preview
        result = {}
        for output_path, template_name in template_files.items():
            # Render the output path (it might contain variables)
            rendered_path = context.render_string(output_path)
            
            # Render the template
            content = self.template_manager.render_template(template_name, context)
            result[rendered_path] = content
            
        return result
    
    def generate_deployment(self, deployment_type: str,
                          output_dir: str,
                          environment_name: Optional[str],
                          context: TemplateContext) -> List[str]:
        """
        Generate deployment files.
        
        Args:
            deployment_type: Type of deployment to generate
            output_dir: Base output directory
            environment_name: Optional environment name to use
            context: Template context with variables
            
        Returns:
            List of generated file paths
        """
        if deployment_type not in self.deployment_registry:
            raise ValueError(f"Deployment type '{deployment_type}' not found")
        
        # Validate required variables
        is_valid, missing_vars = self.validate_deployment_variables(deployment_type, context)
        if not is_valid:
            raise ValueError(f"Missing required variables: {', '.join(missing_vars)}")
        
        # Add environment variables if specified
        if environment_name is not None:
            if environment_name not in self.environment_registry:
                raise ValueError(f"Environment '{environment_name}' not found")
            
            # Create a new context with environment variables
            env_context = TemplateContext(self.environment_registry[environment_name].get('variables', {}))
            
            # Create a new context that inherits from both
            merged_context = TemplateContext(context.context)
            merged_context.inherit_from(env_context)
            context = merged_context
        
        # Get template files
        template_files = self.deployment_registry[deployment_type].get('template_files', {})
        
        # Generate files
        generated_files = []
        for output_path, template_name in template_files.items():
            # Render the output path (it might contain variables)
            rendered_path = context.render_string(output_path)
            full_path = os.path.join(output_dir, rendered_path)
            
            # Render the template to file
            self.template_manager.render_to_file(template_name, full_path, context)
            generated_files.append(full_path)
            
        return generated_files
    
    def generate_service_definition(self, service_name: str, 
                                  service_type: str,
                                  context: TemplateContext) -> Dict[str, Any]:
        """
        Generate a service definition for inclusion in deployment files.
        
        Args:
            service_name: Name of the service
            service_type: Type of service (e.g., web, worker, database)
            context: Template context with variables
            
        Returns:
            Dictionary with service definition
        """
        # Basic service definition
        service_def = {
            'name': service_name,
            'type': service_type
        }
        
        # Add variables from context
        for key, value in context.get_merged_context().items():
            if key.startswith('service_'):
                # Remove 'service_' prefix
                service_key = key[8:]
                service_def[service_key] = value
                
        return service_def
    
    def generate_multi_service_deployment(self, deployment_type: str,
                                        output_dir: str,
                                        environment_name: Optional[str],
                                        services: List[Dict[str, Any]],
                                        global_context: TemplateContext) -> List[str]:
        """
        Generate a deployment with multiple services.
        
        Args:
            deployment_type: Type of deployment to generate
            output_dir: Base output directory
            environment_name: Optional environment name to use
            services: List of service definitions
            global_context: Global template context with variables
            
        Returns:
            List of generated file paths
        """
        if deployment_type not in self.deployment_registry:
            raise ValueError(f"Deployment type '{deployment_type}' not found")
        
        # Create a new context with services
        context = TemplateContext(global_context.context)
        context.set('services', services)
        
        # Generate deployment
        return self.generate_deployment(deployment_type, output_dir, environment_name, context)
