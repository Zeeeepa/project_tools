"""
Code Generator module for LLM integration.

This module provides functionality to generate code using LLMs.
"""

import os
import re
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path
from rich.console import Console
from rich.panel import Panel

from .llm_client import LLMClient
from .context_manager import ProjectContext

console = Console()

class CodeGenerator:
    """Generates code using LLMs."""
    
    def __init__(self, llm_client: LLMClient, project_context: ProjectContext):
        """Initialize code generator.
        
        Args:
            llm_client: LLM client to use for generation.
            project_context: Project context to use for generation.
        """
        self.llm_client = llm_client
        self.project_context = project_context
        
    def generate_component(self, component_type: str, name: str, description: str, 
                          path: Optional[str] = None) -> Tuple[bool, str]:
        """Generate a component.
        
        Args:
            component_type: Type of component (e.g., "frontend", "backend", "model").
            name: Name of the component.
            description: Description of the component.
            path: Optional path to save the component to.
            
        Returns:
            Tuple of (success, file_path).
        """
        console.print(Panel(f"[bold blue]Generating {component_type} component: {name}[/bold blue]"))
        
        # Determine the appropriate path if not provided
        if path is None:
            if component_type == "frontend":
                path = os.path.join("frontend", "src", "components", f"{name}.tsx")
            elif component_type == "backend":
                project_name = self.project_context.project_path.name.replace("-", "_")
                path = os.path.join("src", project_name, f"{name}.py")
            else:
                path = os.path.join(f"{name}.py")
        
        # Create the prompt for the LLM
        prompt = self._create_component_prompt(component_type, name, description)
        
        # Generate the code
        console.print(f"[cyan]Generating code for {name}...[/cyan]")
        code = self.llm_client.generate(prompt)
        
        if not code:
            console.print(f"[red]Failed to generate code for {name}[/red]")
            return False, ""
        
        # Extract the code from the LLM response
        extracted_code = self._extract_code_from_response(code)
        
        if not extracted_code:
            console.print(f"[red]Failed to extract code from LLM response for {name}[/red]")
            return False, ""
        
        # Save the code to the file
        full_path = os.path.join(self.project_context.project_path, path)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        
        try:
            with open(full_path, "w") as f:
                f.write(extracted_code)
            
            console.print(f"[green]Successfully generated {name} at {path}[/green]")
            
            # Add the component to the project context
            self.project_context.add_component(
                component_type=component_type,
                name=name,
                path=path,
                description=description
            )
            
            # Add a history entry
            self.project_context.add_history_entry(
                action="generate",
                description=f"Generated {component_type} component: {name}",
                metadata={
                    "component_type": component_type,
                    "name": name,
                    "path": path
                }
            )
            
            return True, path
        except Exception as e:
            console.print(f"[red]Error saving generated code: {str(e)}[/red]")
            return False, ""
    
    def _create_component_prompt(self, component_type: str, name: str, description: str) -> str:
        """Create a prompt for generating a component.
        
        Args:
            component_type: Type of component.
            name: Name of the component.
            description: Description of the component.
            
        Returns:
            Prompt string.
        """
        project_name = self.project_context.project_path.name
        
        if component_type == "frontend":
            return f"""
You are an expert React/TypeScript developer. Create a React component named {name} for the {project_name} project.

Component Description:
{description}

Requirements:
- Use TypeScript with proper type definitions
- Use modern React practices (hooks, functional components)
- Include proper error handling
- Add comments explaining complex logic
- Make the component reusable and well-structured

Return only the code without any explanations or markdown formatting.
"""
        elif component_type == "backend":
            return f"""
You are an expert Python developer. Create a Python module named {name} for the {project_name} project.

Module Description:
{description}

Requirements:
- Use modern Python 3.9+ features
- Follow PEP 8 style guidelines
- Include proper error handling
- Add docstrings and type hints
- Make the code modular and well-structured

Return only the code without any explanations or markdown formatting.
"""
        else:
            return f"""
You are an expert software developer. Create a {component_type} component named {name} for the {project_name} project.

Component Description:
{description}

Requirements:
- Use best practices for {component_type} development
- Include proper error handling
- Add comments explaining complex logic
- Make the code modular and well-structured

Return only the code without any explanations or markdown formatting.
"""
    
    def _extract_code_from_response(self, response: str) -> str:
        """Extract code from LLM response.
        
        Args:
            response: LLM response string.
            
        Returns:
            Extracted code string.
        """
        # Try to extract code from markdown code blocks
        code_block_pattern = r"```(?:\w+)?\s*([\s\S]+?)\s*```"
        matches = re.findall(code_block_pattern, response)
        
        if matches:
            return matches[0].strip()
        
        # If no code blocks found, return the whole response
        return response.strip()
    
    def generate_from_description(self, description: str) -> List[Dict[str, Any]]:
        """Generate components from a natural language description.
        
        Args:
            description: Natural language description of what to generate.
            
        Returns:
            List of generated components.
        """
        console.print(Panel(f"[bold blue]Generating from description[/bold blue]"))
        
        # First, use the LLM to parse the description into structured requirements
        parsing_prompt = f"""
You are an expert software architect. Parse the following project description into a structured list of components to generate.

Project Description:
{description}

For each component, provide:
1. Component type (frontend, backend, model, etc.)
2. Component name (in camelCase or snake_case as appropriate)
3. Component description
4. Suggested file path

Format your response as a JSON array of objects with the following structure:
[
  {{
    "type": "component_type",
    "name": "component_name",
    "description": "detailed description of what this component should do",
    "path": "suggested/file/path"
  }},
  ...
]

Return only the JSON without any explanations or markdown formatting.
"""
        
        console.print(f"[cyan]Parsing description into components...[/cyan]")
        parsed_response = self.llm_client.generate(parsing_prompt)
        
        try:
            # Extract JSON from the response
            json_pattern = r"\[\s*\{[\s\S]+\}\s*\]"
            json_match = re.search(json_pattern, parsed_response)
            
            if json_match:
                import json
                components_to_generate = json.loads(json_match.group(0))
            else:
                raise ValueError("Failed to extract JSON from LLM response")
                
            # Add the requirements to the project context
            for component in components_to_generate:
                self.project_context.add_requirement(
                    requirement=component["description"],
                    category=component["type"]
                )
            
            # Generate each component
            generated_components = []
            for component in components_to_generate:
                success, path = self.generate_component(
                    component_type=component["type"],
                    name=component["name"],
                    description=component["description"],
                    path=component["path"]
                )
                
                if success:
                    generated_components.append({
                        "type": component["type"],
                        "name": component["name"],
                        "path": path
                    })
            
            return generated_components
        except Exception as e:
            console.print(f"[red]Error generating from description: {str(e)}[/red]")
            return []
