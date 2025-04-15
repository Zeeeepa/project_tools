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
from .runtime_validator import RuntimeValidator, RuntimeValidationResult
from .db_schema_generator import DBSchemaGenerator
from .test_generator import TestGenerator
from .codebase_analyzer import CodebaseAnalyzer
from .error_collector import ErrorCollector
from .feedback_loop import FeedbackLoop

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
        self.runtime_validator = RuntimeValidator(project_path)
        self.db_schema_generator = DBSchemaGenerator(self.llm_client, self.project_context)
        self.test_generator = TestGenerator(self.llm_client, self.project_context)
        self.codebase_analyzer = CodebaseAnalyzer(project_path)
        self.error_collector = ErrorCollector(project_path)
        self.feedback_loop = FeedbackLoop(project_path, self.llm_client)
        
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
    
    def generate_database_schema(self, project_description: str, requirements: List[str], 
                               db_type: str = "PostgreSQL") -> Tuple[bool, str, str]:
        """Generate a database schema.
        
        Args:
            project_description: Description of the project.
            requirements: List of requirements for the schema.
            db_type: Type of database to generate schema for.
            
        Returns:
            Tuple of (success, schema, file_path).
        """
        return self.db_schema_generator.generate_schema(project_description, requirements, db_type)
    
    def generate_sqlalchemy_models(self, schema: str) -> Tuple[bool, str, str]:
        """Generate SQLAlchemy models from a database schema.
        
        Args:
            schema: Database schema to generate models from.
            
        Returns:
            Tuple of (success, models, file_path).
        """
        return self.db_schema_generator.generate_sqlalchemy_models(schema)
    
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
        return self.test_generator.generate_unit_tests(component_path, test_framework, additional_instructions)
    
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
        return self.test_generator.generate_integration_tests(component_paths, test_framework, additional_instructions)
    
    def validate_component(self, path: str) -> ValidationResult:
        """Validate a component.
        
        Args:
            path: Path to the component to validate.
            
        Returns:
            Validation result.
        """
        return self.code_validator.validate_file(path)
    
    def validate_component_runtime(self, path: str, args: List[str] = None) -> RuntimeValidationResult:
        """Validate a component at runtime.
        
        Args:
            path: Path to the component to validate.
            args: Command-line arguments to pass to the script.
            
        Returns:
            Runtime validation result.
        """
        # Determine file type
        file_ext = os.path.splitext(path)[1].lower()
        
        if file_ext == '.py':
            return self.runtime_validator.validate_python_file(path, args)
        elif file_ext in ['.js', '.jsx', '.ts', '.tsx']:
            return self.runtime_validator.validate_javascript_file(path, args)
        else:
            return RuntimeValidationResult(False, errors=[f"Unsupported file type for runtime validation: {file_ext}"])
    
    def validate_function(self, file_path: str, function_name: str, 
                        args: List[Any] = None, kwargs: Dict[str, Any] = None) -> RuntimeValidationResult:
        """Validate a function by executing it.
        
        Args:
            file_path: Path to the file containing the function.
            function_name: Name of the function to validate.
            args: Positional arguments to pass to the function.
            kwargs: Keyword arguments to pass to the function.
            
        Returns:
            Runtime validation result.
        """
        return self.runtime_validator.validate_python_function(file_path, function_name, args, kwargs)
    
    def validate_api_endpoint(self, file_path: str, endpoint: str, method: str = "GET", 
                            data: Dict[str, Any] = None, headers: Dict[str, str] = None) -> RuntimeValidationResult:
        """Validate an API endpoint by making a request to it.
        
        Args:
            file_path: Path to the file containing the API endpoint.
            endpoint: URL of the endpoint to validate.
            method: HTTP method to use.
            data: Data to send with the request.
            headers: Headers to include in the request.
            
        Returns:
            Runtime validation result.
        """
        return self.runtime_validator.validate_api_endpoint(file_path, endpoint, method, data, headers)
    
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
            
            # Add feedback
            for error in errors:
                self.feedback_loop.add_feedback(
                    component_path=path,
                    feedback_type="error",
                    feedback_message=error
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
            
            # Add feedback
            self.feedback_loop.add_feedback(
                component_path=path,
                feedback_type="issue",
                feedback_message=issue_description
            )
            
            console.print(f"[green]Successfully debugged component at {path}[/green]")
            return True
        except Exception as e:
            console.print(f"[red]Error debugging component: {str(e)}[/red]")
            return False
    
    def analyze_codebase(self, include_patterns: List[str] = None, exclude_patterns: List[str] = None) -> Dict[str, Any]:
        """Analyze the codebase.
        
        Args:
            include_patterns: List of glob patterns to include.
            exclude_patterns: List of glob patterns to exclude.
            
        Returns:
            Dictionary of analysis results.
        """
        console.print(Panel(f"[bold blue]Analyzing codebase at {self.project_path}[/bold blue]"))
        
        # Analyze the codebase
        analysis_results = self.codebase_analyzer.analyze_codebase(include_patterns, exclude_patterns)
        
        # Print summary
        summary = analysis_results["summary"]
        console.print(f"[green]Analysis complete:[/green]")
        console.print(f"  Total files: {summary['total_files']}")
        console.print(f"  Total lines of code: {summary['total_lines_of_code']}")
        console.print(f"  Average complexity: {summary['average_complexity']:.2f}")
        
        if summary["architectural_patterns"]:
            console.print(f"  Detected architectural patterns: {', '.join(summary['architectural_patterns'])}")
        
        if summary["improvement_suggestions"]:
            console.print(f"[yellow]Improvement suggestions:[/yellow]")
            for suggestion in summary["improvement_suggestions"]:
                console.print(f"  - [{suggestion['priority']}] {suggestion['description']}")
        
        return analysis_results
    
    def visualize_dependency_graph(self):
        """Visualize the dependency graph of the codebase."""
        tree = self.codebase_analyzer.visualize_dependency_graph()
        console.print(tree)
    
    def export_analysis(self, output_path: str) -> bool:
        """Export analysis results to a file.
        
        Args:
            output_path: Path to save the analysis results.
            
        Returns:
            Whether the export was successful.
        """
        return self.codebase_analyzer.export_analysis(output_path)
    
    def add_feedback(self, component_path: str, feedback_type: str, feedback_message: str) -> str:
        """Add feedback for a component.
        
        Args:
            component_path: Path to the component.
            feedback_type: Type of feedback (e.g., "error", "warning", "suggestion").
            feedback_message: Feedback message.
            
        Returns:
            ID of the added feedback entry.
        """
        return self.feedback_loop.add_feedback(component_path, feedback_type, feedback_message)
    
    def improve_component_from_feedback(self, component_path: str) -> bool:
        """Improve a component based on feedback.
        
        Args:
            component_path: Path to the component.
            
        Returns:
            Whether the improvement was successful.
        """
        return self.feedback_loop.improve_component(component_path)
    
    def generate_feedback_report(self) -> str:
        """Generate a report of feedback.
        
        Returns:
            Report as a string.
        """
        return self.feedback_loop.generate_feedback_report()
    
    def generate_multi_component_project(self, description: str, 
                                       include_database: bool = True,
                                       include_tests: bool = True,
                                       db_type: str = "PostgreSQL") -> List[Dict[str, Any]]:
        """Generate a multi-component project from a description.
        
        This is a higher-level method that orchestrates the generation of multiple
        components, including database schema and tests if requested.
        
        Args:
            description: Description of the project.
            include_database: Whether to generate a database schema.
            include_tests: Whether to generate tests.
            db_type: Type of database to generate schema for.
            
        Returns:
            List of generated components.
        """
        console.print(Panel(f"[bold blue]Project Genie: Generating multi-component project[/bold blue]"))
        
        # Add the description as a requirement
        self.project_context.add_requirement(description, category="user_description")
        
        # Generate components
        components = self.code_generator.generate_from_description(description)
        
        # Generate database schema if requested
        if include_database:
            # Extract requirements from the description
            requirements_prompt = f"""
Extract specific requirements for a database schema from the following project description:

Project Description:
{description}

Return a list of specific requirements for the database schema, one per line.
Each requirement should be a specific piece of information that needs to be stored in the database.
"""
            requirements_response = self.llm_client.generate(requirements_prompt)
            requirements = [req.strip() for req in requirements_response.split('\n') if req.strip()]
            
            # Generate the schema
            success, schema, schema_path = self.generate_database_schema(description, requirements, db_type)
            
            if success:
                # Generate SQLAlchemy models
                success, models, models_path = self.generate_sqlalchemy_models(schema)
                
                if success:
                    components.append({
                        "type": "database_schema",
                        "name": f"{db_type.lower()}_schema",
                        "path": schema_path
                    })
                    
                    components.append({
                        "type": "database_models",
                        "name": "sqlalchemy_models",
                        "path": models_path
                    })
        
        # Generate tests if requested
        if include_tests and components:
            # Generate unit tests for each component
            for component in components:
                if component["type"] in ["frontend", "backend", "database_models"]:
                    success, tests, tests_path = self.generate_unit_tests(component["path"])
                    
                    if success:
                        components.append({
                            "type": "unit_test",
                            "name": f"{component['name']}_test",
                            "path": tests_path
                        })
            
            # Generate integration tests for related components
            if len(components) >= 2:
                # Group components by type
                frontend_components = [c["path"] for c in components if c["type"] == "frontend"]
                backend_components = [c["path"] for c in components if c["type"] == "backend"]
                model_components = [c["path"] for c in components if c["type"] == "database_models"]
                
                # Generate integration tests for frontend-backend interaction
                if frontend_components and backend_components:
                    paths = frontend_components[:1] + backend_components[:1]
                    success, tests, tests_path = self.generate_integration_tests(paths)
                    
                    if success:
                        components.append({
                            "type": "integration_test",
                            "name": "frontend_backend_integration",
                            "path": tests_path
                        })
                
                # Generate integration tests for backend-model interaction
                if backend_components and model_components:
                    paths = backend_components[:1] + model_components[:1]
                    success, tests, tests_path = self.generate_integration_tests(paths)
                    
                    if success:
                        components.append({
                            "type": "integration_test",
                            "name": "backend_model_integration",
                            "path": tests_path
                        })
        
        # Validate and refine components
        for component in components:
            # Syntax validation
            validation_result = self.validate_component(component["path"])
            
            if not validation_result.success:
                console.print(f"[yellow]Component {component['name']} has validation issues:[/yellow]")
                for error in validation_result.errors:
                    console.print(f"[red]  - {error}[/red]")
                
                # Try to refine the component
                refined = self.refine_component(component["path"], validation_result.errors)
                if refined:
                    console.print(f"[green]Successfully refined component {component['name']}[/green]")
            
            # Runtime validation for Python files
            if component["path"].endswith(".py") and component["type"] not in ["unit_test", "integration_test"]:
                try:
                    runtime_result = self.validate_component_runtime(component["path"])
                    
                    if not runtime_result.success:
                        console.print(f"[yellow]Component {component['name']} has runtime issues:[/yellow]")
                        for error in runtime_result.errors:
                            console.print(f"[red]  - {error}[/red]")
                            
                            # Add feedback
                            self.add_feedback(
                                component_path=component["path"],
                                feedback_type="runtime_error",
                                feedback_message=error
                            )
                        
                        # Try to improve the component
                        improved = self.improve_component_from_feedback(component["path"])
                        if improved:
                            console.print(f"[green]Successfully improved component {component['name']}[/green]")
                except Exception as e:
                    console.print(f"[red]Error during runtime validation of {component['name']}: {str(e)}[/red]")
        
        # Analyze the generated codebase
        try:
            self.analyze_codebase()
        except Exception as e:
            console.print(f"[red]Error analyzing codebase: {str(e)}[/red]")
        
        return components
