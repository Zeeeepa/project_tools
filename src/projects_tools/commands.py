import os
import click
import subprocess
import json
from jinja2 import Environment, PackageLoader
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich import print as rprint

# Import our templating system
from .templating import (
    TemplateManager, 
    ComponentGenerator, 
    TemplateContext,
    TemplateRegistry,
    PatternGenerator,
    LayoutGenerator
)
from .templating.algorithms import generate_crud_operations, generate_form_validation

# Initialize Jinja2 environment and rich console
env = Environment(
    loader=PackageLoader('projects_tools', 'templates')
)
console = Console()

# Initialize our templating system
template_manager = TemplateManager(
    package_name='projects_tools',
    template_dir='templates'
)

# Initialize template registry
template_registry = TemplateRegistry()
pattern_registry_path = os.path.join(os.path.dirname(__file__), 'templates', 'patterns', 'pattern_registry.json')
if os.path.exists(pattern_registry_path):
    template_registry.load_from_file(pattern_registry_path)

# Register algorithm generators
template_registry.register_algorithm(
    'generate_crud_operations',
    generate_crud_operations,
    ['model_name', 'fields'],
    {'type': 'python', 'category': 'crud'}
)

template_registry.register_algorithm(
    'generate_form_validation',
    generate_form_validation,
    ['form_name', 'fields'],
    {'type': 'javascript', 'category': 'validation'}
)

# Initialize pattern generator
pattern_generator = PatternGenerator(template_manager, template_registry)

# Initialize component generator
component_generator = ComponentGenerator(template_manager)

# Load component registry
registry_path = os.path.join(os.path.dirname(__file__), 'templates', 'components', 'registry', 'component_registry.json')
if os.path.exists(registry_path):
    component_generator.load_component_registry(registry_path)

# Initialize layout generator
layout_generator = LayoutGenerator(template_manager, template_registry, pattern_generator)

# Load layout registry
layout_registry_path = os.path.join(os.path.dirname(__file__), 'templates', 'layouts', 'layout_registry.json')
if os.path.exists(layout_registry_path):
    layout_generator.load_layouts_from_file(layout_registry_path)

@click.group()
def cli():
    """Project management tools"""
    pass

@cli.command()
@click.argument('project_name')
@click.option('--backend', is_flag=True, help='Create Python backend project')
@click.option('--frontend', is_flag=True, help='Create frontend project')
@click.option('--frontend_type', 
              type=click.Choice(['vue', 'reactjs'], case_sensitive=False),
              default='reactjs',
              help='Frontend type: vue or reactjs (default: reactjs)')
@click.option('--enable_proxy', is_flag=True, help='Enable proxy server for frontend')
@click.option('--llm-assisted', is_flag=True, help='Enable LLM-assisted code generation')
def create(project_name, backend, frontend, frontend_type, enable_proxy, llm_assisted):
    """Create a new project with specified components"""
    if not backend and not frontend:
        console.print("[red]Please specify at least one of --backend or --frontend[/red]")
        return

    console.print(Panel(f"[bold blue]Creating new project: {project_name}[/bold blue]"))

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        # Create project directory
        progress.add_task("Creating project directory...", total=None)
        os.makedirs(project_name, exist_ok=True)
        python_package_name = project_name.replace('-', '_')
        
        if backend:
            console.print("\n[bold cyan]Setting up Python backend:[/bold cyan]")
            
            # Create Python project structure
            task_id = progress.add_task("Creating Python project structure...", total=None)
            os.makedirs(os.path.join(project_name, "src"), exist_ok=True)
            os.makedirs(os.path.join(project_name, "src", project_name), exist_ok=True)
            progress.update(task_id, completed=True)
            
            # Create version.py
            task_id = progress.add_task("Creating version.py...", total=None)
            with open(os.path.join(project_name, "src", project_name, "version.py"), "w") as f:
                f.write('__version__ = "0.1.0"\n')
            progress.update(task_id, completed=True)

            # Create __init__.py
            task_id = progress.add_task("Creating __init__.py...", total=None)
            with open(os.path.join(project_name, "src", project_name, "__init__.py"), "w") as f:
                f.write('')
            progress.update(task_id, completed=True)
            
            # Render and write setup.py using our new templating system
            task_id = progress.add_task("Creating setup.py...", total=None)
            
            # Create template context
            context = TemplateContext({
                'project_name': project_name,
                'python_package_name': python_package_name
            })
            
            # Render template to file
            template_manager.render_to_file(
                'setup.py.jinja2',
                os.path.join(project_name, "setup.py"),
                context
            )
            
            progress.update(task_id, completed=True)
            
        if frontend:
            console.print("\n[bold cyan]Setting up Frontend:[/bold cyan]")
            
            # Render and write Makefile using our new templating system
            task_id = progress.add_task("Creating Makefile...", total=None)
            
            # Create template context
            context = TemplateContext({
                'project_name': project_name,
                'python_package_name': python_package_name
            })
            
            # Render template to file
            template_manager.render_to_file(
                'Makefile.jinja2',
                os.path.join(project_name, "Makefile"),
                context
            )
            
            progress.update(task_id, completed=True)
                
            # Execute frontend setup based on type
            from pathlib import Path
            project_path = Path(project_name)
            
            if frontend_type == 'vue':
                from .vue_tasks import create_vue_project                 
                if not create_vue_project(project_name, project_path):
                    return
            else:
                from .react_tasks import create_react_project
                if not create_react_project(project_name, project_path):
                    return
        
        # Render and write deploy.sh using our new templating system
        task_id = progress.add_task("Creating deploy.sh...", total=None)
        
        # Create template context
        context = TemplateContext({
            'project_name': project_name,
            'python_package_name': python_package_name
        })
        
        # Render template to file
        template_manager.render_to_file(
            'deploy.sh.jinja2',
            os.path.join(project_name, "deploy.sh"),
            context
        )
        
        # Make deploy.sh executable
        os.chmod(os.path.join(project_name, "deploy.sh"), 0o755)
        
        progress.update(task_id, completed=True)
        
        # Create .gitignore
        task_id = progress.add_task("Creating .gitignore...", total=None)
        with open(os.path.join(project_name, ".gitignore"), "w") as f:
            f.write("web/\nlogs/\n__pycache__/\ndist/\nbuild/\npasted/\n")
        progress.update(task_id, completed=True)

        if enable_proxy:
            # Create proxy.py using our new templating system
            task_id = progress.add_task("Creating proxy server...", total=None)
            
            # Create template context
            context = TemplateContext({
                'project_name': project_name,
                'python_package_name': python_package_name,
                'frontend': frontend,
                'vue': frontend_type == "vue"
            })
            
            # Render template to file
            template_manager.render_to_file(
                'proxy.py.jinja2',
                os.path.join(project_name, "src", project_name, "proxy.py"),
                context
            )
            
            progress.update(task_id, completed=True)
        
        # Render and write README.md using our new templating system
        task_id = progress.add_task("Creating README.md...", total=None)
        
        # Create template context
        context = TemplateContext({
            'project_name': project_name
        })
        
        # Render template to file
        template_manager.render_to_file(
            'README.md.jinja2',
            os.path.join(project_name, "README.md"),
            context
        )
        
        progress.update(task_id, completed=True)
        
    console.print(Panel(f"[bold green]Successfully created project: {project_name}[/bold green]"))

    # If LLM-assisted mode is enabled, set up the LLM integration
    if llm_assisted:
        console.print("\n[bold cyan]Setting up LLM integration:[/bold cyan]")
        
        # Create requirements.txt with LLM dependencies
        with open(os.path.join(project_name, "requirements.txt"), "a") as f:
            f.write("\n# LLM integration dependencies\nrequests>=2.28.0\n")
        
        console.print("[green]Added LLM dependencies to requirements.txt[/green]")
        console.print(Panel("[bold yellow]To use LLM-assisted features, set your API keys as environment variables:[/bold yellow]\n\nFor OpenAI: export OPENAI_API_KEY=your_key_here\nFor Anthropic: export ANTHROPIC_API_KEY=your_key_here"))


@cli.command()
@click.argument('description')
@click.option('--project-path', default=".", help='Path to the project')
@click.option('--llm-provider', 
              type=click.Choice(['openai', 'anthropic'], case_sensitive=False),
              default='openai',
              help='LLM provider to use (default: openai)')
def genie(description, project_path, llm_provider):
    """Generate code based on natural language description"""
    console.print(Panel(f"[bold blue]Project Genie: Generating from description[/bold blue]"))
    
    try:
        from .llm_integration import ProjectGenie
        
        genie = ProjectGenie(project_path, llm_provider)
        components = genie.generate_from_description(description)
        
        console.print(f"[green]Successfully generated {len(components)} components:[/green]")
        for component in components:
            console.print(f"- {component['name']}: {component['path']}")
    except ImportError:
        console.print("[red]Error: LLM integration module not found.[/red]")
        console.print("[yellow]Make sure you have the required dependencies installed:[/yellow]")
        console.print("pip install requests")
    except Exception as e:
        console.print(f"[red]Error generating code: {str(e)}[/red]")


@cli.command()
@click.argument('component_path')
@click.argument('issue_description')
@click.option('--project-path', default=".", help='Path to the project')
@click.option('--llm-provider', 
              type=click.Choice(['openai', 'anthropic'], case_sensitive=False),
              default='openai',
              help='LLM provider to use (default: openai)')
def debug(component_path, issue_description, project_path, llm_provider):
    """Debug a component based on issue description"""
    console.print(Panel(f"[bold blue]Debugging component: {component_path}[/bold blue]"))
    
    try:
        from .llm_integration import ProjectGenie
        
        genie = ProjectGenie(project_path, llm_provider)
        success = genie.debug_component(component_path, issue_description)
        
        if success:
            console.print(f"[green]Successfully debugged component: {component_path}[/green]")
        else:
            console.print(f"[red]Failed to debug component: {component_path}[/red]")
    except ImportError:
        console.print("[red]Error: LLM integration module not found.[/red]")
        console.print("[yellow]Make sure you have the required dependencies installed:[/yellow]")
        console.print("pip install requests")
    except Exception as e:
        console.print(f"[red]Error debugging component: {str(e)}[/red]")


@cli.command()
@click.argument('project_path', default=".")
@click.option('--include-patterns', '-i', multiple=True, help='Glob patterns to include')
@click.option('--exclude-patterns', '-e', multiple=True, help='Glob patterns to exclude')
@click.option('--output-file', '-o', help='Path to save analysis results')
@click.option('--llm-provider', 
              type=click.Choice(['openai', 'anthropic'], case_sensitive=False),
              default='openai',
              help='LLM provider to use (default: openai)')
def analyze_codebase(project_path, include_patterns, exclude_patterns, output_file, llm_provider):
    """Analyze a codebase and generate insights"""
    console.print(Panel(f"[bold blue]Analyzing codebase: {project_path}[/bold blue]"))
    
    try:
        from .llm_integration import ProjectGenie
        
        genie = ProjectGenie(project_path, llm_provider)
        
        # Convert include/exclude patterns to lists
        include_patterns_list = list(include_patterns) if include_patterns else None
        exclude_patterns_list = list(exclude_patterns) if exclude_patterns else None
        
        # Analyze the codebase
        analysis_results = genie.analyze_codebase(include_patterns_list, exclude_patterns_list)
        
        # Visualize the dependency graph
        console.print("\n[bold cyan]Dependency Graph:[/bold cyan]")
        genie.visualize_dependency_graph()
        
        # Export analysis results if requested
        if output_file:
            if genie.export_analysis(output_file):
                console.print(f"[green]Analysis results exported to {output_file}[/green]")
    except ImportError:
        console.print("[red]Error: LLM integration module not found.[/red]")
        console.print("[yellow]Make sure you have the required dependencies installed:[/yellow]")
        console.print("pip install requests")
    except Exception as e:
        console.print(f"[red]Error analyzing codebase: {str(e)}[/red]")


@cli.command()
@click.argument('component_name')
@click.option('--output-dir', '-o', default=".", help='Output directory')
@click.option('--module-name', '-m', required=True, help='Module name')
@click.option('--module-description', '-d', required=True, help='Module description')
@click.option('--class-name', '-c', required=True, help='Class name')
@click.option('--data-type', '-t', help='Data type (for data processor component)')
@click.option('--preview', is_flag=True, help='Preview the component without generating files')
def generate_component(component_name, output_dir, module_name, module_description, class_name, data_type, preview):
    """Generate a component from a template"""
    console.print(Panel(f"[bold blue]Generating component: {component_name}[/bold blue]"))
    
    # Create template context
    context = TemplateContext({
        'module_name': module_name,
        'module_description': module_description,
        'class_name': class_name,
        'class_name_variable': class_name.lower(),
        'output_dir': output_dir
    })
    
    # Add data_type if provided
    if data_type:
        context.set('data_type', data_type)
    
    try:
        if preview:
            # Generate component preview
            previews = component_generator.generate_component_preview(component_name, context)
            
            console.print(f"[green]Component preview for {component_name}:[/green]")
            for path, content in previews.items():
                console.print(f"\n[bold cyan]File: {path}[/bold cyan]")
                console.print(content)
        else:
            # Generate component
            generated_files = component_generator.generate_component(component_name, output_dir, context)
            
            console.print(f"[green]Successfully generated component {component_name}:[/green]")
            for file_path in generated_files:
                console.print(f"- {file_path}")
    except ValueError as e:
        console.print(f"[red]Error generating component: {str(e)}[/red]")
    except Exception as e:
        console.print(f"[red]Error generating component: {str(e)}[/red]")


@cli.command()
def list_components():
    """List available components"""
    console.print(Panel(f"[bold blue]Available Components[/bold blue]"))
    
    # List base components
    base_components = component_generator.list_base_components()
    console.print("\n[bold cyan]Base Components:[/bold cyan]")
    for component in base_components:
        console.print(f"- {component['name']}: {component['description']}")
        if component.get('required_vars'):
            console.print(f"  Required variables: {', '.join(component['required_vars'])}")
    
    # List derived components
    components = component_generator.list_components()
    console.print("\n[bold cyan]Derived Components:[/bold cyan]")
    for component in components:
        console.print(f"- {component['name']}: {component['description']}")
        if component.get('base_component'):
            console.print(f"  Based on: {component['base_component']}")


@cli.command()
@click.argument('pattern_id')
@click.option('--output-file', '-o', help='Output file path')
@click.option('--module-name', '-m', required=True, help='Module name')
@click.option('--module-description', '-d', required=True, help='Module description')
@click.option('--class-name', '-c', required=True, help='Class name')
@click.option('--data-type', '-t', help='Data type (for data processor component)')
def generate_from_pattern(pattern_id, output_file, module_name, module_description, class_name, data_type):
    """Generate content from a pattern"""
    console.print(Panel(f"[bold blue]Generating from pattern: {pattern_id}[/bold blue]"))
    
    # Create template context
    context = TemplateContext({
        'module_name': module_name,
        'module_description': module_description,
        'class_name': class_name,
        'class_name_variable': class_name.lower()
    })
    
    # Add data_type if provided
    if data_type:
        context.set('data_type', data_type)
    
    try:
        # Generate content
        content = pattern_generator.generate_from_pattern(pattern_id, context, output_file)
        
        if output_file:
            console.print(f"[green]Successfully generated content to {output_file}[/green]")
        else:
            console.print(f"[green]Generated content:[/green]")
            console.print(content)
    except ValueError as e:
        console.print(f"[red]Error generating content: {str(e)}[/red]")
    except Exception as e:
        console.print(f"[red]Error generating content: {str(e)}[/red]")


@cli.command()
def list_patterns():
    """List available patterns"""
    console.print(Panel(f"[bold blue]Available Patterns[/bold blue]"))
    
    # List templates
    templates = template_registry.list_templates()
    console.print("\n[bold cyan]Templates:[/bold cyan]")
    for template in templates:
        console.print(f"- {template['id']}: {template['path']}")
        if template.get('metadata'):
            metadata_str = ", ".join([f"{k}: {v}" for k, v in template['metadata'].items()])
            console.print(f"  Metadata: {metadata_str}")
    
    # List patterns
    patterns = template_registry.list_patterns()
    console.print("\n[bold cyan]Patterns:[/bold cyan]")
    for pattern in patterns:
        console.print(f"- {pattern['id']}")
        if pattern.get('variables'):
            console.print(f"  Variables: {', '.join(pattern['variables'])}")
        if pattern.get('metadata'):
            metadata_str = ", ".join([f"{k}: {v}" for k, v in pattern['metadata'].items()])
            console.print(f"  Metadata: {metadata_str}")
    
    # List algorithms
    algorithms = template_registry.list_algorithms()
    console.print("\n[bold cyan]Algorithms:[/bold cyan]")
    for algorithm in algorithms:
        console.print(f"- {algorithm['id']}")
        if algorithm.get('parameters'):
            console.print(f"  Parameters: {', '.join(algorithm['parameters'])}")
        if algorithm.get('metadata'):
            metadata_str = ", ".join([f"{k}: {v}" for k, v in algorithm['metadata'].items()])
            console.print(f"  Metadata: {metadata_str}")


@cli.command()
@click.argument('layout_id')
@click.option('--output-dir', '-o', default=".", help='Output directory')
@click.option('--module-name', '-m', required=True, help='Module name')
@click.option('--module-description', '-d', required=True, help='Module description')
@click.option('--class-name', '-c', required=True, help='Class name')
@click.option('--data-type', '-t', help='Data type (for data processor component)')
@click.option('--preview', is_flag=True, help='Preview the layout without generating files')
def generate_layout(layout_id, output_dir, module_name, module_description, class_name, data_type, preview):
    """Generate a layout"""
    console.print(Panel(f"[bold blue]Generating layout: {layout_id}[/bold blue]"))
    
    # Create template context
    context = TemplateContext({
        'module_name': module_name,
        'module_description': module_description,
        'class_name': class_name,
        'class_name_variable': class_name.lower()
    })
    
    # Add data_type if provided
    if data_type:
        context.set('data_type', data_type)
    
    try:
        if preview:
            # Generate layout preview
            previews = layout_generator.generate_layout_preview(layout_id, context)
            
            console.print(f"[green]Layout preview for {layout_id}:[/green]")
            for path, content in previews.items():
                console.print(f"\n[bold cyan]File: {path}[/bold cyan]")
                console.print(content)
        else:
            # Generate layout
            generated_files = layout_generator.generate_layout(layout_id, context, output_dir)
            
            console.print(f"[green]Successfully generated layout {layout_id}:[/green]")
            for file_path in generated_files:
                console.print(f"- {file_path}")
    except ValueError as e:
        console.print(f"[red]Error generating layout: {str(e)}[/red]")
    except Exception as e:
        console.print(f"[red]Error generating layout: {str(e)}[/red]")


@cli.command()
def list_layouts():
    """List available layouts"""
    console.print(Panel(f"[bold blue]Available Layouts[/bold blue]"))
    
    # List layouts
    layouts = layout_generator.list_layouts()
    for layout in layouts:
        console.print(f"- {layout['id']}: {layout['description']}")
        console.print(f"  Components: {layout['component_count']}")


@cli.command()
@click.argument('algorithm_id')
@click.option('--output-file', '-o', help='Output file path')
@click.option('--model-name', '-m', required=True, help='Model name')
@click.option('--fields-json', '-f', required=True, help='JSON string of fields')
def generate_from_algorithm(algorithm_id, output_file, model_name, fields_json):
    """Generate content from an algorithm"""
    console.print(Panel(f"[bold blue]Generating from algorithm: {algorithm_id}[/bold blue]"))
    
    try:
        # Parse fields JSON
        fields = json.loads(fields_json)
        
        # Generate content
        if algorithm_id == 'generate_crud_operations':
            content = pattern_generator.generate_from_algorithm(
                algorithm_id,
                {'model_name': model_name, 'fields': fields},
                output_file
            )
        elif algorithm_id == 'generate_form_validation':
            content = pattern_generator.generate_from_algorithm(
                algorithm_id,
                {'form_name': model_name, 'fields': fields},
                output_file
            )
        else:
            raise ValueError(f"Unknown algorithm: {algorithm_id}")
        
        if output_file:
            console.print(f"[green]Successfully generated content to {output_file}[/green]")
        else:
            console.print(f"[green]Generated content:[/green]")
            console.print(content)
    except ValueError as e:
        console.print(f"[red]Error generating content: {str(e)}[/red]")
    except Exception as e:
        console.print(f"[red]Error generating content: {str(e)}[/red]")


@cli.command()
@click.option('--metadata-key', '-k', required=True, help='Metadata key')
@click.option('--metadata-value', '-v', required=True, help='Metadata value')
@click.option('--output-dir', '-o', help='Output directory')
@click.option('--module-name', '-m', required=True, help='Module name')
@click.option('--module-description', '-d', required=True, help='Module description')
@click.option('--class-name', '-c', required=True, help='Class name')
def generate_by_metadata(metadata_key, metadata_value, output_dir, module_name, module_description, class_name):
    """Generate content by metadata"""
    console.print(Panel(f"[bold blue]Generating content by metadata: {metadata_key}={metadata_value}[/bold blue]"))
    
    # Create template context
    context = TemplateContext({
        'module_name': module_name,
        'module_description': module_description,
        'class_name': class_name,
        'class_name_variable': class_name.lower()
    })
    
    try:
        # Generate content
        generated = pattern_generator.find_and_generate(metadata_key, metadata_value, context, output_dir)
        
        if output_dir:
            console.print(f"[green]Successfully generated content to {output_dir}:[/green]")
            for item_id in generated:
                console.print(f"- {item_id}")
        else:
            console.print(f"[green]Generated content:[/green]")
            for item_id, content in generated.items():
                console.print(f"\n[bold cyan]{item_id}:[/bold cyan]")
                console.print(content)
    except ValueError as e:
        console.print(f"[red]Error generating content: {str(e)}[/red]")
    except Exception as e:
        console.print(f"[red]Error generating content: {str(e)}[/red]")
