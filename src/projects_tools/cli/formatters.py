"""
Output formatters for the CLI.

This module provides formatters for CLI output using rich.
"""

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.tree import Tree
from rich.syntax import Syntax
from rich.progress import Progress, SpinnerColumn, TextColumn
from typing import List, Dict, Any, Optional, Union

# Initialize console
console = Console()


def print_success(message: str) -> None:
    """
    Print a success message.

    Args:
        message: Message to print.
    """
    console.print(Panel(f"[bold green]{message}[/bold green]"))


def print_error(message: str) -> None:
    """
    Print an error message.

    Args:
        message: Message to print.
    """
    console.print(Panel(f"[bold red]{message}[/bold red]"))


def print_warning(message: str) -> None:
    """
    Print a warning message.

    Args:
        message: Message to print.
    """
    console.print(Panel(f"[bold yellow]{message}[/bold yellow]"))


def print_info(message: str) -> None:
    """
    Print an info message.

    Args:
        message: Message to print.
    """
    console.print(Panel(f"[bold blue]{message}[/bold blue]"))


def print_code(code: str, language: str = "python") -> None:
    """
    Print code with syntax highlighting.

    Args:
        code: Code to print.
        language: Language for syntax highlighting.
    """
    syntax = Syntax(code, language, theme="monokai", line_numbers=True)
    console.print(syntax)


def print_table(
    title: str,
    columns: List[str],
    rows: List[List[str]],
    caption: Optional[str] = None,
) -> None:
    """
    Print a table.

    Args:
        title: Title of the table.
        columns: Column names.
        rows: Table rows.
        caption: Optional caption for the table.
    """
    table = Table(title=title, caption=caption)
    
    for column in columns:
        table.add_column(column)
    
    for row in rows:
        table.add_row(*row)
    
    console.print(table)


def print_tree(
    title: str,
    data: Dict[str, Any],
    guide_style: str = "bold bright_blue",
) -> None:
    """
    Print a tree.

    Args:
        title: Title of the tree.
        data: Tree data.
        guide_style: Style for the tree guides.
    """
    tree = Tree(f"[bold]{title}[/bold]", guide_style=guide_style)
    
    def add_branch(branch, data):
        if isinstance(data, dict):
            for key, value in data.items():
                if isinstance(value, (dict, list)):
                    sub_branch = branch.add(f"[bold]{key}[/bold]")
                    add_branch(sub_branch, value)
                else:
                    branch.add(f"[bold]{key}[/bold]: {value}")
        elif isinstance(data, list):
            for i, item in enumerate(data):
                if isinstance(item, (dict, list)):
                    sub_branch = branch.add(f"[bold]{i}[/bold]")
                    add_branch(sub_branch, item)
                else:
                    branch.add(f"{i}: {item}")
    
    add_branch(tree, data)
    console.print(tree)


def create_progress(description: str = "") -> Progress:
    """
    Create a progress bar.

    Args:
        description: Description for the progress bar.

    Returns:
        Progress instance.
    """
    return Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    )


def print_components(components: List[Dict[str, Any]]) -> None:
    """
    Print a list of components.

    Args:
        components: List of components.
    """
    if not components:
        console.print("[yellow]No components found.[/yellow]")
        return
    
    console.print(f"[green]Found {len(components)} components:[/green]")
    
    for component in components:
        name = component.get("name", "Unknown")
        path = component.get("path", "Unknown")
        component_type = component.get("type", "Unknown")
        
        console.print(f"- [bold]{name}[/bold] ({component_type}): {path}")


def print_analysis_results(results: Dict[str, Any]) -> None:
    """
    Print analysis results.

    Args:
        results: Analysis results.
    """
    if not results:
        console.print("[yellow]No analysis results found.[/yellow]")
        return
    
    summary = results.get("summary", {})
    
    console.print(Panel(f"[bold blue]Analysis Results[/bold blue]"))
    
    console.print(f"[green]Summary:[/green]")
    console.print(f"  Total files: {summary.get('total_files', 0)}")
    console.print(f"  Total lines of code: {summary.get('total_lines_of_code', 0)}")
    console.print(f"  Average complexity: {summary.get('average_complexity', 0):.2f}")
    
    patterns = summary.get("architectural_patterns", [])
    if patterns:
        console.print(f"  Detected architectural patterns: {', '.join(patterns)}")
    
    suggestions = summary.get("improvement_suggestions", [])
    if suggestions:
        console.print(f"[yellow]Improvement suggestions:[/yellow]")
        for suggestion in suggestions:
            priority = suggestion.get("priority", "medium")
            description = suggestion.get("description", "")
            console.print(f"  - [{priority}] {description}")
