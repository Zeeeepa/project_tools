"""
Test Generator module for LLM integration.

This module provides functionality to generate tests using LLMs.
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

class TestGenerator:
    """Generates tests using LLMs."""
    
    def __init__(self, llm_client: LLMClient, project_context: ProjectContext):
        """Initialize test generator.
        
        Args:
            llm_client: LLM client to use for generation.
            project_context: Project context to use for generation.
        """
        self.llm_client = llm_client
        self.project_context = project_context
        self._setup_templates()
        
    def _setup_templates(self):
        """Set up Jinja2 templates for test generation."""
        # Create templates directory if it doesn't exist
        templates_dir = os.path.join(os.path.dirname(__file__), "templates")
        os.makedirs(templates_dir, exist_ok=True)
        
        # Create unit test template if it doesn't exist
        unit_test_template_path = os.path.join(templates_dir, "unit_test.jinja")
        if not os.path.exists(unit_test_template_path):
            with open(unit_test_template_path, "w") as f:
                f.write("""
You are a test engineer. Create unit tests for the following component:

Project Name: {{ project_name }}

Component Type: {{ component_type }}
Component Name: {{ component_name }}
Component Path: {{ component_path }}

Component Code:
```
{{ component_code }}
```

Please provide comprehensive unit tests in {{ test_framework }} format, following these guidelines:
1. Cover all public methods and functions
2. Include edge cases and error conditions
3. Use mocks and fixtures where appropriate
4. Add docstrings explaining the purpose of each test
5. Follow best practices for {{ test_framework }}

{% if additional_instructions %}
Additional Instructions:
{{ additional_instructions }}
{% endif %}
                """.strip())
        
        # Create integration test template if it doesn't exist
        integration_test_template_path = os.path.join(templates_dir, "integration_test.jinja")
        if not os.path.exists(integration_test_template_path):
            with open(integration_test_template_path, "w") as f:
                f.write("""
You are a test engineer. Create integration tests for the following components:

Project Name: {{ project_name }}

Components to test:
{% for component in components %}
- {{ component.name }} ({{ component.type }}): {{ component.path }}
{% endfor %}

Please provide integration tests in {{ test_framework }} format, following these guidelines:
1. Test the interactions between components
2. Include happy path and error scenarios
3. Use appropriate setup and teardown
4. Add docstrings explaining the purpose of each test
5. Follow best practices for {{ test_framework }}

{% if additional_instructions %}
Additional Instructions:
{{ additional_instructions }}
{% endif %}
                """.strip())
        
        # Load templates
        self.env = Environment(loader=FileSystemLoader(templates_dir))
        
    def generate_unit_tests(self, component_path: str, test_framework: str = "pytest", 
                           additional_instructions: str = "") -> Tuple[bool, str, str]:
        """Generate unit tests for a component.
        
        Args:
            component_path: Path to the component to test.
            test_framework: Test framework to use.
            additional_instructions: Additional instructions for test generation.
            
        Returns:
            Tuple of (success, tests, file_path).
        """
        console.print(Panel(f"[bold blue]Generating unit tests for {component_path}[/bold blue]"))
        
        # Get project name
        project_name = self.project_context.project_path.name
        
        # Get component details
        full_component_path = os.path.join(self.project_context.project_path, component_path)
        if not os.path.exists(full_component_path):
            console.print(f"[red]Component not found at {full_component_path}[/red]")
            return False, "", ""
        
        # Read component code
        with open(full_component_path, "r") as f:
            component_code = f.read()
        
        # Determine component type and name
        component_type = "unknown"
        if component_path.endswith(".py"):
            component_type = "python"
        elif component_path.endswith(".js") or component_path.endswith(".jsx"):
            component_type = "javascript"
        elif component_path.endswith(".ts") or component_path.endswith(".tsx"):
            component_type = "typescript"
        
        component_name = os.path.basename(component_path).split(".")[0]
        
        # Create the prompt using Jinja2 template
        template = self.env.get_template("unit_test.jinja")
        prompt = template.render(
            project_name=project_name,
            component_type=component_type,
            component_name=component_name,
            component_path=component_path,
            component_code=component_code,
            test_framework=test_framework,
            additional_instructions=additional_instructions
        )
        
        # Generate the tests
        console.print(f"[cyan]Generating unit tests...[/cyan]")
        tests = self.llm_client.generate(prompt, max_tokens=2000)
        
        if not tests:
            console.print(f"[red]Failed to generate unit tests[/red]")
            return False, "", ""
        
        # Extract code from the response
        code_block_pattern = r"```(?:python|javascript|typescript)?\s*([\s\S]+?)```"
        matches = re.findall(code_block_pattern, tests)
        
        if matches:
            tests_code = matches[0].strip()
        else:
            tests_code = tests.strip()
        
        # Determine the test file path
        test_dir = os.path.join(self.project_context.project_path, "tests")
        os.makedirs(test_dir, exist_ok=True)
        
        # Create appropriate test filename
        if component_type == "python":
            test_filename = f"test_{component_name}.py"
        else:
            test_filename = f"{component_name}.test.{component_path.split('.')[-1]}"
        
        file_path = os.path.join(test_dir, test_filename)
        
        try:
            with open(file_path, "w") as f:
                f.write(tests_code)
            
            console.print(f"[green]Successfully generated unit tests at {file_path}[/green]")
            
            # Add the tests to the project context
            self.project_context.add_component(
                component_type="unit_test",
                name=f"{component_name}_test",
                path=file_path,
                description=f"Unit tests for {component_name}"
            )
            
            # Add a history entry
            self.project_context.add_history_entry(
                action="generate",
                description=f"Generated unit tests for {component_name}",
                metadata={
                    "component_type": "unit_test",
                    "name": f"{component_name}_test",
                    "path": file_path
                }
            )
            
            return True, tests_code, file_path
        except Exception as e:
            console.print(f"[red]Error saving generated tests: {str(e)}[/red]")
            return False, tests_code, ""
    
    def generate_integration_tests(self, component_paths: List[str], test_framework: str = "pytest",
                                 additional_instructions: str = "") -> Tuple[bool, str, str]:
        """Generate integration tests for multiple components.
        
        Args:
            component_paths: Paths to the components to test.
            test_framework: Test framework to use.
            additional_instructions: Additional instructions for test generation.
            
        Returns:
            Tuple of (success, tests, file_path).
        """
        console.print(Panel(f"[bold blue]Generating integration tests for {len(component_paths)} components[/bold blue]"))
        
        # Get project name
        project_name = self.project_context.project_path.name
        
        # Get component details
        components = []
        for path in component_paths:
            full_path = os.path.join(self.project_context.project_path, path)
            if not os.path.exists(full_path):
                console.print(f"[yellow]Warning: Component not found at {full_path}[/yellow]")
                continue
            
            # Determine component type
            component_type = "unknown"
            if path.endswith(".py"):
                component_type = "python"
            elif path.endswith(".js") or path.endswith(".jsx"):
                component_type = "javascript"
            elif path.endswith(".ts") or path.endswith(".tsx"):
                component_type = "typescript"
            
            component_name = os.path.basename(path).split(".")[0]
            
            components.append({
                "name": component_name,
                "type": component_type,
                "path": path
            })
        
        if not components:
            console.print(f"[red]No valid components found[/red]")
            return False, "", ""
        
        # Create the prompt using Jinja2 template
        template = self.env.get_template("integration_test.jinja")
        prompt = template.render(
            project_name=project_name,
            components=components,
            test_framework=test_framework,
            additional_instructions=additional_instructions
        )
        
        # Generate the tests
        console.print(f"[cyan]Generating integration tests...[/cyan]")
        tests = self.llm_client.generate(prompt, max_tokens=2000)
        
        if not tests:
            console.print(f"[red]Failed to generate integration tests[/red]")
            return False, "", ""
        
        # Extract code from the response
        code_block_pattern = r"```(?:python|javascript|typescript)?\s*([\s\S]+?)```"
        matches = re.findall(code_block_pattern, tests)
        
        if matches:
            tests_code = matches[0].strip()
        else:
            tests_code = tests.strip()
        
        # Determine the test file path
        test_dir = os.path.join(self.project_context.project_path, "tests")
        os.makedirs(test_dir, exist_ok=True)
        
        # Create appropriate test filename
        component_names = "_".join([c["name"] for c in components[:2]])
        if len(components) > 2:
            component_names += "_etc"
        
        if components[0]["type"] == "python":
            test_filename = f"test_integration_{component_names}.py"
        else:
            test_filename = f"integration_{component_names}.test.{component_paths[0].split('.')[-1]}"
        
        file_path = os.path.join(test_dir, test_filename)
        
        try:
            with open(file_path, "w") as f:
                f.write(tests_code)
            
            console.print(f"[green]Successfully generated integration tests at {file_path}[/green]")
            
            # Add the tests to the project context
            self.project_context.add_component(
                component_type="integration_test",
                name=f"integration_{component_names}",
                path=file_path,
                description=f"Integration tests for {component_names}"
            )
            
            # Add a history entry
            self.project_context.add_history_entry(
                action="generate",
                description=f"Generated integration tests for {component_names}",
                metadata={
                    "component_type": "integration_test",
                    "name": f"integration_{component_names}",
                    "path": file_path
                }
            )
            
            return True, tests_code, file_path
        except Exception as e:
            console.print(f"[red]Error saving generated tests: {str(e)}[/red]")
            return False, tests_code, ""
