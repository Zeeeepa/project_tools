"""
Project Genie module for LLM integration.

This module provides the main interface for LLM-assisted project generation.
"""

import os
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path
from rich.console import Console
from rich.panel import Panel

from .llm_client import LLMClient, get_llm_client
from .context_manager import ProjectContext
from .code_generator import CodeGenerator
from .validator import CodeValidator, ValidationResult

console = Console()

class ProjectGenie:
    """Main class for LLM-assisted project generation."""
    
    def __init__(self, project_path: str, llm_provider: str = "openai"):
        """Initialize Project Genie.
        
        Args:
            project_path: Path to the project directory.
            llm_provider: LLM provider to use. One of "openai" or "anthropic".
        """
        self.project_path = Path(project_path)
        self.llm_client = get_llm_client(llm_provider)
        self.project_context = ProjectContext(project_path)
        self.code_generator = CodeGenerator(self.llm_client, self.project_context)
        self.code_validator = CodeValidator(project_path)
        
    def generate_from_description(self, description: str) -> List[Dict[str, Any]]:
        """Generate components from a natural language description.
        
        Args:
            description: Natural language description of what to generate.
            
        Returns:
            List of generated components.
        """
        console.print(Panel(f"[bold blue]Project Genie: Generating from description[/bold blue]"))
        
        # Add the description as a requirement
        self.project_context.add_requirement(description, category="user_description")
        
        # Generate components
        components = self.code_generator.generate_from_description(description)
        
        # Validate components
        for component in components:
            validation_result = self.validate_component(component["path"])
            
            if not validation_result.success:
                console.print(f"[yellow]Warning: Component {component['name']} has validation issues:[/yellow]")
                for error in validation_result.errors:
                    console.print(f"[red]  - {error}[/red]")
                for warning in validation_result.warnings:
                    console.print(f"[yellow]  - {warning}[/yellow]")
                
                # Try to refine the component
                refined = self.refine_component(component["path"], validation_result.errors)
                if refined:
                    console.print(f"[green]Successfully refined component {component['name']}[/green]")
        
        return components
    
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
        return self.code_generator.generate_component(component_type, name, description, path)
    
    def validate_component(self, path: str) -> ValidationResult:
        """Validate a component.
        
        Args:
            path: Path to the component to validate.
            
        Returns:
            Validation result.
        """
        return self.code_validator.validate_file(path)
    
    def refine_component(self, path: str, errors: List[str]) -> bool:
        """Refine a component based on validation errors.
        
        Args:
            path: Path to the component to refine.
            errors: List of validation errors.
            
        Returns:
            Whether the refinement was successful.
        """
        console.print(f"[cyan]Refining component at {path}...[/cyan]")
        
        full_path = os.path.join(self.project_path, path)
        
        try:
            with open(full_path, 'r') as f:
                original_code = f.read()
            
            # Create a prompt for refinement
            prompt = f"""
You are an expert software developer. Refine the following code to fix these errors:

Errors:
{chr(10).join(f"- {error}" for error in errors)}

Code to refine:
```
{original_code}
```

Return only the refined code without any explanations or markdown formatting.
"""
            
            # Generate refined code
            refined_code = self.llm_client.generate(prompt)
            
            # Extract the code from the LLM response
            refined_code = self.code_generator._extract_code_from_response(refined_code)
            
            if not refined_code:
                console.print(f"[red]Failed to generate refined code for {path}[/red]")
                return False
            
            # Save the refined code
            with open(full_path, 'w') as f:
                f.write(refined_code)
            
            # Add a history entry
            self.project_context.add_history_entry(
                action="refine",
                description=f"Refined component at {path}",
                metadata={
                    "path": path,
                    "errors": errors
                }
            )
            
            # Validate the refined code
            validation_result = self.validate_component(path)
            
            if validation_result.success:
                console.print(f"[green]Successfully refined component at {path}[/green]")
                return True
            else:
                console.print(f"[yellow]Component at {path} still has validation issues after refinement[/yellow]")
                return False
        except Exception as e:
            console.print(f"[red]Error refining component: {str(e)}[/red]")
            return False
    
    def debug_component(self, path: str, issue_description: str) -> bool:
        """Debug a component based on a description of the issue.
        
        Args:
            path: Path to the component to debug.
            issue_description: Description of the issue.
            
        Returns:
            Whether the debugging was successful.
        """
        console.print(f"[cyan]Debugging component at {path}...[/cyan]")
        
        full_path = os.path.join(self.project_path, path)
        
        try:
            with open(full_path, 'r') as f:
                original_code = f.read()
            
            # Create a prompt for debugging
            prompt = f"""
You are an expert software developer. Debug the following code based on this issue description:

Issue Description:
{issue_description}

Code to debug:
```
{original_code}
```

Return only the fixed code without any explanations or markdown formatting.
"""
            
            # Generate debugged code
            debugged_code = self.llm_client.generate(prompt)
            
            # Extract the code from the LLM response
            debugged_code = self.code_generator._extract_code_from_response(debugged_code)
            
            if not debugged_code:
                console.print(f"[red]Failed to generate debugged code for {path}[/red]")
                return False
            
            # Save the debugged code
            with open(full_path, 'w') as f:
                f.write(debugged_code)
            
            # Add a history entry
            self.project_context.add_history_entry(
                action="debug",
                description=f"Debugged component at {path}",
                metadata={
                    "path": path,
                    "issue_description": issue_description
                }
            )
            
            console.print(f"[green]Successfully debugged component at {path}[/green]")
            return True
        except Exception as e:
            console.print(f"[red]Error debugging component: {str(e)}[/red]")
            return False
