"""
Database Schema Generator module for LLM integration.

This module provides functionality to generate database schemas using LLMs.
"""

import os
import re
import json
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from jinja2 import Environment, FileSystemLoader, Template

from .llm_client import LLMClient
from .context_manager import ProjectContext

console = Console()

class DBSchemaGenerator:
    """Generates database schemas using LLMs."""
    
    def __init__(self, llm_client: LLMClient, project_context: ProjectContext):
        """Initialize database schema generator.
        
        Args:
            llm_client: LLM client to use for generation.
            project_context: Project context to use for generation.
        """
        self.llm_client = llm_client
        self.project_context = project_context
        self._setup_templates()
        
    def _setup_templates(self):
        """Set up Jinja2 templates for schema generation."""
        # Create templates directory if it doesn't exist
        templates_dir = os.path.join(os.path.dirname(__file__), "templates")
        os.makedirs(templates_dir, exist_ok=True)
        
        # Create schema template if it doesn't exist
        schema_template_path = os.path.join(templates_dir, "db_schema.jinja")
        if not os.path.exists(schema_template_path):
            with open(schema_template_path, "w") as f:
                f.write("""
You are a database architect. Create a database schema for the following project:

Project Name: {{ project_name }}

Project Description:
{{ project_description }}

Requirements:
{% for requirement in requirements %}
- {{ requirement }}
{% endfor %}

Please provide the schema in the following format:
1. Entity-Relationship Diagram (text-based)
2. SQL DDL statements for creating the tables
3. Explanation of the schema design decisions

For SQL, use {{ db_type }} syntax.
                """.strip())
        
        # Create SQLAlchemy model template if it doesn't exist
        sqlalchemy_template_path = os.path.join(templates_dir, "sqlalchemy_models.jinja")
        if not os.path.exists(sqlalchemy_template_path):
            with open(sqlalchemy_template_path, "w") as f:
                f.write("""
You are a Python developer. Create SQLAlchemy models for the following database schema:

Project Name: {{ project_name }}

Database Schema:
{{ schema }}

Please provide the SQLAlchemy models in Python code format, following these guidelines:
1. Use SQLAlchemy ORM syntax
2. Include proper type annotations
3. Add docstrings for each class and method
4. Include relationships between models
5. Add __repr__ methods for each model
                """.strip())
        
        # Load templates
        self.env = Environment(loader=FileSystemLoader(templates_dir))
        
    def generate_schema(self, project_description: str, requirements: List[str], 
                        db_type: str = "PostgreSQL") -> Tuple[bool, str, str]:
        """Generate a database schema.
        
        Args:
            project_description: Description of the project.
            requirements: List of requirements for the schema.
            db_type: Type of database to generate schema for.
            
        Returns:
            Tuple of (success, schema, file_path).
        """
        console.print(Panel(f"[bold blue]Generating database schema for {db_type}[/bold blue]"))
        
        # Get project name
        project_name = self.project_context.project_path.name
        
        # Create the prompt using Jinja2 template
        template = self.env.get_template("db_schema.jinja")
        prompt = template.render(
            project_name=project_name,
            project_description=project_description,
            requirements=requirements,
            db_type=db_type
        )
        
        # Generate the schema
        console.print(f"[cyan]Generating database schema...[/cyan]")
        schema = self.llm_client.generate(prompt, max_tokens=2000)
        
        if not schema:
            console.print(f"[red]Failed to generate database schema[/red]")
            return False, "", ""
        
        # Save the schema to a file
        schema_dir = os.path.join(self.project_context.project_path, "database")
        os.makedirs(schema_dir, exist_ok=True)
        
        file_path = os.path.join(schema_dir, f"{db_type.lower()}_schema.sql")
        
        try:
            with open(file_path, "w") as f:
                f.write(schema)
            
            console.print(f"[green]Successfully generated database schema at {file_path}[/green]")
            
            # Add the schema to the project context
            self.project_context.add_component(
                component_type="database_schema",
                name=f"{db_type.lower()}_schema",
                path=file_path,
                description=f"Database schema for {project_name} using {db_type}"
            )
            
            # Add a history entry
            self.project_context.add_history_entry(
                action="generate",
                description=f"Generated database schema using {db_type}",
                metadata={
                    "component_type": "database_schema",
                    "name": f"{db_type.lower()}_schema",
                    "path": file_path
                }
            )
            
            return True, schema, file_path
        except Exception as e:
            console.print(f"[red]Error saving generated schema: {str(e)}[/red]")
            return False, schema, ""
    
    def generate_sqlalchemy_models(self, schema: str) -> Tuple[bool, str, str]:
        """Generate SQLAlchemy models from a database schema.
        
        Args:
            schema: Database schema to generate models from.
            
        Returns:
            Tuple of (success, models, file_path).
        """
        console.print(Panel(f"[bold blue]Generating SQLAlchemy models[/bold blue]"))
        
        # Get project name
        project_name = self.project_context.project_path.name
        
        # Create the prompt using Jinja2 template
        template = self.env.get_template("sqlalchemy_models.jinja")
        prompt = template.render(
            project_name=project_name,
            schema=schema
        )
        
        # Generate the models
        console.print(f"[cyan]Generating SQLAlchemy models...[/cyan]")
        models = self.llm_client.generate(prompt, max_tokens=2000)
        
        if not models:
            console.print(f"[red]Failed to generate SQLAlchemy models[/red]")
            return False, "", ""
        
        # Extract Python code from the response
        code_block_pattern = r"```(?:python)?\s*([\s\S]+?)```"
        matches = re.findall(code_block_pattern, models)
        
        if matches:
            models_code = matches[0].strip()
        else:
            models_code = models.strip()
        
        # Save the models to a file
        models_dir = os.path.join(self.project_context.project_path, "database")
        os.makedirs(models_dir, exist_ok=True)
        
        file_path = os.path.join(models_dir, "models.py")
        
        try:
            with open(file_path, "w") as f:
                f.write(models_code)
            
            console.print(f"[green]Successfully generated SQLAlchemy models at {file_path}[/green]")
            
            # Add the models to the project context
            self.project_context.add_component(
                component_type="database_models",
                name="sqlalchemy_models",
                path=file_path,
                description=f"SQLAlchemy models for {project_name}"
            )
            
            # Add a history entry
            self.project_context.add_history_entry(
                action="generate",
                description=f"Generated SQLAlchemy models",
                metadata={
                    "component_type": "database_models",
                    "name": "sqlalchemy_models",
                    "path": file_path
                }
            )
            
            return True, models_code, file_path
        except Exception as e:
            console.print(f"[red]Error saving generated models: {str(e)}[/red]")
            return False, models_code, ""
