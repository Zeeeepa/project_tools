"""
CLI commands for projects_tools.

This module provides the CLI commands for projects_tools.
"""

import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import click

from ..utils.config import config, init_config
from ..utils.errors import ProjectCreationError, ValidationError, format_error
from .formatters import (
    console,
    create_progress,
    print_analysis_results,
    print_components,
    print_error,
    print_info,
    print_success,
    print_warning,
)
from .validators import (
    validate_component_path,
    validate_db_type,
    validate_feedback_type,
    validate_frontend_type,
    validate_llm_provider,
    validate_project_name,
    validate_project_path,
)

# Initialize configuration
init_config()


@click.group()
@click.version_option()
def cli():
    """Project management tools."""
    pass


@cli.command()
@click.argument("project_name")
@click.option("--backend", is_flag=True, help="Create Python backend project")
@click.option("--frontend", is_flag=True, help="Create frontend project")
@click.option(
    "--frontend_type",
    type=click.Choice(["vue", "reactjs"], case_sensitive=False),
    default=None,
    help="Frontend type: vue or reactjs (default: from config)",
)
@click.option("--enable_proxy", is_flag=True, help="Enable proxy server for frontend")
@click.option("--llm-assisted", is_flag=True, help="Enable LLM-assisted code generation")
def create(project_name, backend, frontend, frontend_type, enable_proxy, llm_assisted):
    """Create a new project with specified components."""
    from ..core.project import ProjectManager

    try:
        # Validate inputs
        project_name = validate_project_name(project_name)

        if frontend_type is None:
            frontend_type = config.get("project.default_frontend", "reactjs")
        else:
            frontend_type = validate_frontend_type(frontend_type)

        if not backend and not frontend:
            print_warning("Please specify at least one of --backend or --frontend")
            return

        print_info(f"Creating new project: {project_name}")

        # Create project manager
        project_manager = ProjectManager()

        # Create project
        with create_progress() as progress:
            task_id = progress.add_task("Creating project...", total=None)

            project = project_manager.create_project(
                name=project_name,
                backend=backend,
                frontend=frontend,
                frontend_type=frontend_type,
                enable_proxy=enable_proxy,
                llm_assisted=llm_assisted,
                progress=progress,
            )

            progress.update(task_id, completed=True)

        print_success(f"Successfully created project: {project_name}")

        # Print project info
        print_info(f"Project path: {project.path}")

        if llm_assisted:
            print_warning(
                "To use LLM-assisted features, set your API keys as environment variables:\n\n"
                "For OpenAI: export OPENAI_API_KEY=your_key_here\n"
                "For Anthropic: export ANTHROPIC_API_KEY=your_key_here"
            )

    except ValidationError as e:
        print_error(format_error(e))
    except ProjectCreationError as e:
        print_error(format_error(e))
    except Exception as e:
        print_error(f"Unexpected error: {str(e)}")


@cli.command()
@click.argument("description")
@click.option("--project-path", default=".", help="Path to the project")
@click.option(
    "--llm-provider",
    type=click.Choice(["openai", "anthropic"], case_sensitive=False),
    default=None,
    help="LLM provider to use (default: from config)",
)
def genie(description, project_path, llm_provider):
    """Generate code based on natural language description."""
    from ..llm.generator import CodeGenerator

    try:
        # Validate inputs
        project_path = validate_project_path(project_path)

        if llm_provider is None:
            llm_provider = config.get("llm.default_provider", "openai")
        else:
            llm_provider = validate_llm_provider(llm_provider)

        print_info(f"Project Genie: Generating from description")

        # Create code generator
        generator = CodeGenerator(project_path, llm_provider)

        # Generate components
        components = generator.generate_from_description(description)

        # Print components
        print_components(components)

    except ValidationError as e:
        print_error(format_error(e))
    except Exception as e:
        print_error(f"Error generating code: {str(e)}")


@cli.command()
@click.argument("component_path")
@click.argument("issue_description")
@click.option("--project-path", default=".", help="Path to the project")
@click.option(
    "--llm-provider",
    type=click.Choice(["openai", "anthropic"], case_sensitive=False),
    default=None,
    help="LLM provider to use (default: from config)",
)
def debug(component_path, issue_description, project_path, llm_provider):
    """Debug a component based on issue description."""
    from ..llm.generator import CodeGenerator

    try:
        # Validate inputs
        project_path = validate_project_path(project_path)
        component_path = validate_component_path(component_path, str(project_path))

        if llm_provider is None:
            llm_provider = config.get("llm.default_provider", "openai")
        else:
            llm_provider = validate_llm_provider(llm_provider)

        print_info(f"Project Genie: Debugging component")

        # Create code generator
        generator = CodeGenerator(project_path, llm_provider)

        # Debug component
        success = generator.debug_component(component_path, issue_description)

        if success:
            print_success(f"Successfully debugged component at {component_path}")
        else:
            print_error(f"Failed to debug component at {component_path}")

    except ValidationError as e:
        print_error(format_error(e))
    except Exception as e:
        print_error(f"Error debugging component: {str(e)}")


@cli.command()
@click.argument("project_path", default=".")
@click.option("--include-patterns", "-i", multiple=True, help="Glob patterns to include")
@click.option("--exclude-patterns", "-e", multiple=True, help="Glob patterns to exclude")
@click.option("--output-file", "-o", help="Path to save analysis results")
@click.option(
    "--llm-provider",
    type=click.Choice(["openai", "anthropic"], case_sensitive=False),
    default=None,
    help="LLM provider to use (default: from config)",
)
@click.option(
    "--visualization",
    "-v",
    type=click.Choice([
        "dependency", "react", "inheritance", "module", 
        "blast-radius", "http", "usage"
    ], case_sensitive=False),
    default="dependency",
    help="Type of visualization to generate",
)
@click.option(
    "--target-file",
    help="Target file for blast radius visualization",
)
@click.option(
    "--symbol-name",
    help="Symbol name for usage relationship visualization",
)
@click.option(
    "--root-component",
    help="Root component for React component tree visualization",
)
def analyze_codebase(
    project_path, include_patterns, exclude_patterns, output_file, 
    llm_provider, visualization, target_file, symbol_name, root_component
):
    """Analyze a codebase and generate insights."""
    from ..llm_integration.codebase_analyzer import CodebaseAnalyzer

    try:
        # Validate inputs
        project_path = validate_project_path(project_path)

        if llm_provider is None:
            llm_provider = config.get("llm.default_provider", "openai")
        else:
            llm_provider = validate_llm_provider(llm_provider)

        print_info(f"Analyzing codebase at {project_path}")

        # Create analyzer
        analyzer = CodebaseAnalyzer(project_path)

        # Convert include/exclude patterns to lists
        include_patterns_list = list(include_patterns) if include_patterns else None
        exclude_patterns_list = list(exclude_patterns) if exclude_patterns else None

        # Analyze the codebase
        analysis_results = analyzer.analyze_codebase(include_patterns_list, exclude_patterns_list)

        # Print analysis results
        print_analysis_results(analysis_results)

        # Generate the requested visualization
        print_info(f"Generating {visualization} visualization...")
        
        if visualization == "dependency":
            # Visualize the dependency graph
            analyzer.visualize_dependency_graph()
        elif visualization == "react":
            # Visualize React component tree
            result = analyzer.visualize_react_component_tree(root_component)
            print_info(f"React Component Tree (Root: {result.get('root_component')})")
            print_info(f"Component Count: {result.get('component_count')}")
        elif visualization == "inheritance":
            # Visualize inheritance graph
            result = analyzer.visualize_inheritance_graph()
            print_info(f"Class Inheritance Hierarchy")
            print_info(f"Class Count: {result.get('class_count')}")
            print_info(f"Root Classes: {', '.join(result.get('root_classes', []))}")
        elif visualization == "module":
            # Visualize module dependencies
            result = analyzer.visualize_module_dependency()
            print_info(f"Module Dependency Graph")
            print_info(f"Module Count: {result.get('module_count')}")
            print_info(f"Dependency Count: {result.get('dependency_count')}")
        elif visualization == "blast-radius":
            # Validate target file
            if not target_file:
                print_error("Target file is required for blast radius visualization")
                return
            
            # Visualize blast radius
            result = analyzer.visualize_blast_radius(target_file)
            print_info(f"Blast Radius for {target_file}")
            print_info(f"Direct Impact: {result.get('direct_impact')} files")
            print_info(f"Indirect Impact: {result.get('indirect_impact')} files")
            print_info(f"Total Impact: {result.get('total_impact')} files ({result.get('impact_percentage')}% of codebase)")
        elif visualization == "http":
            # Visualize HTTP endpoints
            result = analyzer.visualize_http_endpoints()
            print_info(f"HTTP Endpoints")
            print_info(f"Endpoint Count: {result.get('endpoint_count')}")
            
            # Print methods breakdown
            methods = result.get('methods', {})
            if methods:
                print_info("HTTP Methods:")
                for method, count in methods.items():
                    print_info(f"  {method}: {count}")
        elif visualization == "usage":
            # Visualize usage relationships
            result = analyzer.visualize_usage_relationships(symbol_name)
            if symbol_name:
                print_info(f"Symbol Usage: {symbol_name}")
            else:
                print_info(f"Top Symbol Usages")
            print_info(f"Symbol Count: {result.get('symbol_count')}")
            print_info(f"File Count: {result.get('file_count')}")

        # Export analysis results if requested
        if output_file:
            if analyzer.export_analysis(output_file):
                print_success(f"Analysis results exported to {output_file}")

    except ValidationError as e:
        print_error(format_error(e))
    except Exception as e:
        print_error(f"Error analyzing codebase: {str(e)}")


@cli.command()
@click.option("--config-file", "-c", help="Path to configuration file")
@click.option("--show", "-s", is_flag=True, help="Show current configuration")
@click.option(
    "--set", "-S", "set_values", nargs=2, multiple=True, help="Set configuration value (key value)"
)
@click.option("--save", is_flag=True, help="Save configuration to file")
def configure(config_file, show, set_values, save):
    """Configure projects_tools."""
    from ..utils.config import config

    try:
        # Load configuration from file if specified
        if config_file:
            if config.load_from_file(config_file):
                print_success(f"Loaded configuration from {config_file}")
            else:
                print_error(f"Failed to load configuration from {config_file}")

        # Set configuration values
        for key, value in set_values:
            # Convert value to appropriate type
            if value.lower() in ("true", "yes", "1"):
                value = True
            elif value.lower() in ("false", "no", "0"):
                value = False
            elif value.isdigit():
                value = int(value)
            elif value.replace(".", "", 1).isdigit() and value.count(".") == 1:
                value = float(value)

            config.set(key, value)
            print_success(f"Set {key} = {value}")

        # Show configuration
        if show:
            print_info("Current configuration:")
            for key, value in config.as_dict().items():
                if isinstance(value, dict):
                    print(f"{key}:")
                    for subkey, subvalue in value.items():
                        print(f"  {subkey}: {subvalue}")
                else:
                    print(f"{key}: {value}")

        # Save configuration
        if save:
            if config.save_to_file():
                print_success("Configuration saved")
            else:
                print_error("Failed to save configuration")

    except Exception as e:
        print_error(f"Error configuring projects_tools: {str(e)}")


def main():
    """Entry point for the CLI."""
    cli()


if __name__ == "__main__":
    main()
