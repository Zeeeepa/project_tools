import os
import click
import subprocess
from jinja2 import Environment, PackageLoader
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich import print as rprint

# Initialize Jinja2 environment and rich console
env = Environment(
    loader=PackageLoader('projects_tools', 'templates')
)
console = Console()

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
            
            # Render and write setup.py
            task_id = progress.add_task("Creating setup.py...", total=None)
            setup_template = env.get_template('setup.py.jinja2')
            # Replace hyphens with underscores for Python package name            
            setup_content = setup_template.render(project_name=project_name, python_package_name=python_package_name)
            with open(os.path.join(project_name, "setup.py"), "w") as f:
                f.write(setup_content)
            progress.update(task_id, completed=True)
            
        if frontend:
            console.print("\n[bold cyan]Setting up Frontend:[/bold cyan]")
            
            # Render and write Makefile
            task_id = progress.add_task("Creating Makefile...", total=None)
            makefile_template = env.get_template('Makefile.jinja2')
            makefile_content = makefile_template.render(project_name=project_name, python_package_name=python_package_name)
            with open(os.path.join(project_name, "Makefile"), "w") as f:
                f.write(makefile_content)
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
        
        # Render and write deploy.sh
        task_id = progress.add_task("Creating deploy.sh...", total=None)
        deploy_template = env.get_template('deploy.sh.jinja2')
        deploy_content = deploy_template.render(project_name=project_name, python_package_name=python_package_name)
        with open(os.path.join(project_name, "deploy.sh"), "w") as f:
            f.write(deploy_content)
        os.chmod(os.path.join(project_name, "deploy.sh"), 0o755)
        progress.update(task_id, completed=True)
        
        # Create .gitignore
        task_id = progress.add_task("Creating .gitignore...", total=None)
        with open(os.path.join(project_name, ".gitignore"), "w") as f:
            f.write("web/\nlogs/\n__pycache__/\ndist/\nbuild/\npasted/\n")
        progress.update(task_id, completed=True)

        if enable_proxy:
            # Create proxy.py
            task_id = progress.add_task("Creating proxy server...", total=None)
            proxy_template = env.get_template('proxy.py.jinja2')
            proxy_content = proxy_template.render(
                project_name=project_name, 
                frontend=frontend, 
                python_package_name=python_package_name,
                vue=frontend_type == "vue"
            )
            with open(os.path.join(project_name, "src", project_name, "proxy.py"), "w") as f:
                f.write(proxy_content)
            progress.update(task_id, completed=True)
        
        # Render and write README.md
        task_id = progress.add_task("Creating README.md...", total=None)
        readme_template = env.get_template('README.md.jinja2')
        readme_content = readme_template.render(project_name=project_name)
        with open(os.path.join(project_name, "README.md"), "w") as f:
            f.write(readme_content)
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
@click.option('--project-path', default=".", help='Path to create the project')
@click.option('--llm-provider', 
              type=click.Choice(['openai', 'anthropic'], case_sensitive=False),
              default='openai',
              help='LLM provider to use (default: openai)')
@click.option('--include-database/--no-database', default=True, 
              help='Include database schema and models (default: True)')
@click.option('--include-tests/--no-tests', default=True, 
              help='Include unit and integration tests (default: True)')
@click.option('--db-type', 
              type=click.Choice(['PostgreSQL', 'MySQL', 'SQLite'], case_sensitive=False),
              default='PostgreSQL',
              help='Database type to use (default: PostgreSQL)')
def create_full_project(project_name, description, project_path, llm_provider, 
                      include_database, include_tests, db_type):
    """Create a full project with multiple components based on a description"""
    console.print(Panel(f"[bold blue]Creating full project: {project_name}[/bold blue]"))
    
    try:
        # Create the project directory
        full_project_path = os.path.join(project_path, project_name)
        os.makedirs(full_project_path, exist_ok=True)
        
        # Initialize basic project structure
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            # Create basic structure
            task_id = progress.add_task("Creating basic project structure...", total=None)
            os.makedirs(os.path.join(full_project_path, "src"), exist_ok=True)
            os.makedirs(os.path.join(full_project_path, "tests"), exist_ok=True)
            
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
