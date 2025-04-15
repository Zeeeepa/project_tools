import os
import click
import subprocess
from jinja2 import Environment, PackageLoader
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich import print as rprint

# Import our new templating system
from .templating import TemplateManager, ComponentGenerator, TemplateContext

# Initialize Jinja2 environment and rich console
env = Environment(
    loader=PackageLoader('projects_tools', 'templates')
)
console = Console()

# Initialize our new templating system
template_manager = TemplateManager(
    package_name='projects_tools',
    template_dir='templates'
)

# Initialize component generator
component_generator = ComponentGenerator(template_manager)

# Load component registry
registry_path = os.path.join(os.path.dirname(__file__), 'templates', 'components', 'registry', 'component_registry.json')
if os.path.exists(registry_path):
    component_generator.load_component_registry(registry_path)

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
    console.print(Panel(f"[bold blue]Project Genie: Debugging component[/bold blue]"))
    
    try:
        from .llm_integration import ProjectGenie
        
        genie = ProjectGenie(project_path, llm_provider)
        success = genie.debug_component(component_path, issue_description)
        
        if success:
            console.print(f"[green]Successfully debugged component at {component_path}[/green]")
        else:
            console.print(f"[red]Failed to debug component at {component_path}[/red]")
    except ImportError:
        console.print("[red]Error: LLM integration module not found.[/red]")
        console.print("[yellow]Make sure you have the required dependencies installed:[/yellow]")
        console.print("pip install requests")
    except Exception as e:
        console.print(f"[red]Error debugging component: {str(e)}[/red]")


@cli.command()
@click.argument('project_name')
@click.argument('description')
@click.option('--output-path', default=".", help='Path to create the project in')
@click.option('--include-database', is_flag=True, help='Include database setup')
@click.option('--include-tests', is_flag=True, help='Include test setup')
@click.option('--db-type', 
              type=click.Choice(['SQLite', 'PostgreSQL', 'MySQL'], case_sensitive=False),
              default='SQLite',
              help='Database type to use (default: SQLite)')
@click.option('--llm-provider', 
              type=click.Choice(['openai', 'anthropic'], case_sensitive=False),
              default='openai',
              help='LLM provider to use (default: openai)')
def create_full_project(project_name, description, output_path, include_database, include_tests, db_type, llm_provider):
    """Create a full project with LLM-generated components"""
    console.print(Panel(f"[bold blue]Creating full project: {project_name}[/bold blue]"))
    
    try:
        # Create project directory
        full_project_path = os.path.join(output_path, project_name)
        os.makedirs(full_project_path, exist_ok=True)
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task_id = progress.add_task("Setting up project structure...", total=None)
            
            # Create basic project structure
            os.makedirs(os.path.join(full_project_path, "src"), exist_ok=True)
            os.makedirs(os.path.join(full_project_path, "tests"), exist_ok=True)
            os.makedirs(os.path.join(full_project_path, "docs"), exist_ok=True)
            
            # Create README.md
            with open(os.path.join(full_project_path, "README.md"), "w") as f:
                f.write(f"# {project_name}\n\n{description}\n")
            
            # Create .gitignore
            with open(os.path.join(full_project_path, ".gitignore"), "w") as f:
                f.write("__pycache__/\n*.py[cod]\n*$py.class\n.env\nvenv/\nnode_modules/\ndist/\nbuild/\n")
            
            # Create requirements.txt
            with open(os.path.join(full_project_path, "requirements.txt"), "w") as f:
                f.write("# LLM integration dependencies\nrequests>=2.28.0\n")
                if include_database:
                    f.write("\n# Database dependencies\nsqlalchemy>=2.0.0\n")
                    if db_type == "PostgreSQL":
                        f.write("psycopg2-binary>=2.9.0\n")
                    elif db_type == "MySQL":
                        f.write("pymysql>=1.0.0\n")
            
            progress.update(task_id, completed=True)
        
        # Generate the project components using LLM
        from .llm_integration import ProjectGenie
        
        console.print("\n[bold cyan]Generating project components with LLM:[/bold cyan]")
        
        genie = ProjectGenie(full_project_path, llm_provider)
        components = genie.generate_multi_component_project(
            description=description,
            include_database=include_database,
            include_tests=include_tests,
            db_type=db_type
        )
        
        console.print(f"[green]Successfully generated {len(components)} components:[/green]")
        for component in components:
            console.print(f"- {component['type']}: {component['path']}")
        
        console.print(Panel(f"[bold green]Successfully created full project: {project_name}[/bold green]"))
        console.print(f"[cyan]Project path: {full_project_path}[/cyan]")
        
    except ImportError:
        console.print("[red]Error: LLM integration module not found.[/red]")
        console.print("[yellow]Make sure you have the required dependencies installed:[/yellow]")
        console.print("pip install requests")
    except Exception as e:
        console.print(f"[red]Error creating full project: {str(e)}[/red]")

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
    console.print(Panel(f"[bold blue]Analyzing codebase at {project_path}[/bold blue]"))
    
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
@click.argument('component_path')
@click.option('--args', '-a', multiple=True, help='Arguments to pass to the component')
@click.option('--project-path', default=".", help='Path to the project')
@click.option('--llm-provider', 
              type=click.Choice(['openai', 'anthropic'], case_sensitive=False),
              default='openai',
              help='LLM provider to use (default: openai)')
def validate_runtime(component_path, args, project_path, llm_provider):
    """Validate a component at runtime"""
    console.print(Panel(f"[bold blue]Runtime validation of {component_path}[/bold blue]"))
    
    try:
        from .llm_integration import ProjectGenie
        
        genie = ProjectGenie(project_path, llm_provider)
        
        # Convert args to list
        args_list = list(args) if args else None
        
        # Validate the component
        result = genie.validate_component_runtime(component_path, args_list)
        
        if result.success:
            console.print(f"[green]Runtime validation successful[/green]")
            if result.output:
                console.print(f"[cyan]Output:[/cyan]\n{result.output}")
            console.print(f"[cyan]Execution time: {result.execution_time:.2f}s[/cyan]")
        else:
            console.print(f"[red]Runtime validation failed:[/red]")
            for error in result.errors:
                console.print(f"[red]  - {error}[/red]")
            if result.output:
                console.print(f"[cyan]Output:[/cyan]\n{result.output}")
    except ImportError:
        console.print("[red]Error: LLM integration module not found.[/red]")
        console.print("[yellow]Make sure you have the required dependencies installed:[/yellow]")
        console.print("pip install requests")
    except Exception as e:
        console.print(f"[red]Error validating component: {str(e)}[/red]")


@cli.command()
@click.argument('component_path')
@click.argument('feedback_type', type=click.Choice(['error', 'warning', 'suggestion', 'issue']))
@click.argument('feedback_message')
@click.option('--project-path', default=".", help='Path to the project')
@click.option('--llm-provider', 
              type=click.Choice(['openai', 'anthropic'], case_sensitive=False),
              default='openai',
              help='LLM provider to use (default: openai)')
def add_feedback(component_path, feedback_type, feedback_message, project_path, llm_provider):
    """Add feedback for a component"""
    console.print(Panel(f"[bold blue]Adding feedback for {component_path}[/bold blue]"))
    
    try:
        from .llm_integration import ProjectGenie
        
        genie = ProjectGenie(project_path, llm_provider)
        
        # Add feedback
        entry_id = genie.add_feedback(component_path, feedback_type, feedback_message)
        
        console.print(f"[green]Feedback added with ID: {entry_id}[/green]")
    except ImportError:
        console.print("[red]Error: LLM integration module not found.[/red]")
        console.print("[yellow]Make sure you have the required dependencies installed:[/yellow]")
        console.print("pip install requests")
    except Exception as e:
        console.print(f"[red]Error adding feedback: {str(e)}[/red]")


@cli.command()
@click.argument('component_path')
@click.option('--project-path', default=".", help='Path to the project')
@click.option('--llm-provider', 
              type=click.Choice(['openai', 'anthropic'], case_sensitive=False),
              default='openai',
              help='LLM provider to use (default: openai)')
def improve_component(component_path, project_path, llm_provider):
    """Improve a component based on feedback"""
    console.print(Panel(f"[bold blue]Improving component {component_path}[/bold blue]"))
    
    try:
        from .llm_integration import ProjectGenie
        
        genie = ProjectGenie(project_path, llm_provider)
        
        # Improve the component
        success = genie.improve_component_from_feedback(component_path)
        
        if success:
            console.print(f"[green]Successfully improved component {component_path}[/green]")
        else:
            console.print(f"[yellow]Failed to improve component {component_path}[/yellow]")
    except ImportError:
        console.print("[red]Error: LLM integration module not found.[/red]")
        console.print("[yellow]Make sure you have the required dependencies installed:[/yellow]")
        console.print("pip install requests")
    except Exception as e:
        console.print(f"[red]Error improving component: {str(e)}[/red]")


@cli.command()
@click.option('--project-path', default=".", help='Path to the project')
@click.option('--output-file', '-o', help='Path to save the report')
@click.option('--llm-provider', 
              type=click.Choice(['openai', 'anthropic'], case_sensitive=False),
              default='openai',
              help='LLM provider to use (default: openai)')
def generate_feedback_report(project_path, output_file, llm_provider):
    """Generate a report of feedback"""
    console.print(Panel(f"[bold blue]Generating feedback report[/bold blue]"))
    
    try:
        from .llm_integration import ProjectGenie
        
        genie = ProjectGenie(project_path, llm_provider)
        
        # Generate the report
        report = genie.generate_feedback_report()
        
        # Print the report
        console.print(report)
        
        # Save the report if requested
        if output_file:
            with open(output_file, 'w') as f:
                f.write(report)
            console.print(f"[green]Report saved to {output_file}[/green]")
    except ImportError:
        console.print("[red]Error: LLM integration module not found.[/red]")
        console.print("[yellow]Make sure you have the required dependencies installed:[/yellow]")
        console.print("pip install requests")
    except Exception as e:
        console.print(f"[red]Error generating feedback report: {str(e)}[/red]")

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
