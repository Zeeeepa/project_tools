"""
Error Collector module for LLM integration.

This module provides functionality to collect and analyze errors.
"""

import os
import re
import json
import hashlib
from typing import Dict, List, Optional, Any, Tuple, Set
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()

class ErrorPattern:
    """Represents a pattern of errors."""
    
    def __init__(self, pattern_id: str, pattern: str, description: str, 
                examples: List[str] = None, fix_suggestions: List[str] = None):
        """Initialize error pattern.
        
        Args:
            pattern_id: ID of the pattern.
            pattern: Regular expression pattern to match errors.
            description: Description of the error pattern.
            examples: Examples of errors that match the pattern.
            fix_suggestions: Suggestions for fixing the error.
        """
        self.pattern_id = pattern_id
        self.pattern = pattern
        self.description = description
        self.examples = examples or []
        self.fix_suggestions = fix_suggestions or []
        self.compiled_pattern = re.compile(pattern)
    
    def matches(self, error: str) -> bool:
        """Check if an error matches this pattern.
        
        Args:
            error: Error message to check.
            
        Returns:
            Whether the error matches this pattern.
        """
        return bool(self.compiled_pattern.search(error))
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary.
        
        Returns:
            Dictionary representation of the error pattern.
        """
        return {
            "pattern_id": self.pattern_id,
            "pattern": self.pattern,
            "description": self.description,
            "examples": self.examples,
            "fix_suggestions": self.fix_suggestions
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ErrorPattern':
        """Create from dictionary.
        
        Args:
            data: Dictionary representation of the error pattern.
            
        Returns:
            ErrorPattern instance.
        """
        return cls(
            pattern_id=data["pattern_id"],
            pattern=data["pattern"],
            description=data["description"],
            examples=data.get("examples", []),
            fix_suggestions=data.get("fix_suggestions", [])
        )


class ErrorInstance:
    """Represents an instance of an error."""
    
    def __init__(self, error_id: str, error_message: str, file_path: str = None, 
                line_number: int = None, column_number: int = None, 
                context: str = None, timestamp: float = None):
        """Initialize error instance.
        
        Args:
            error_id: ID of the error.
            error_message: Error message.
            file_path: Path to the file where the error occurred.
            line_number: Line number where the error occurred.
            column_number: Column number where the error occurred.
            context: Context of the error (e.g., surrounding code).
            timestamp: Timestamp of when the error occurred.
        """
        self.error_id = error_id
        self.error_message = error_message
        self.file_path = file_path
        self.line_number = line_number
        self.column_number = column_number
        self.context = context
        self.timestamp = timestamp
        self.matched_patterns = []  # type: List[str]
    
    def add_matched_pattern(self, pattern_id: str):
        """Add a matched pattern.
        
        Args:
            pattern_id: ID of the pattern that matched this error.
        """
        if pattern_id not in self.matched_patterns:
            self.matched_patterns.append(pattern_id)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary.
        
        Returns:
            Dictionary representation of the error instance.
        """
        return {
            "error_id": self.error_id,
            "error_message": self.error_message,
            "file_path": self.file_path,
            "line_number": self.line_number,
            "column_number": self.column_number,
            "context": self.context,
            "timestamp": self.timestamp,
            "matched_patterns": self.matched_patterns
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ErrorInstance':
        """Create from dictionary.
        
        Args:
            data: Dictionary representation of the error instance.
            
        Returns:
            ErrorInstance instance.
        """
        instance = cls(
            error_id=data["error_id"],
            error_message=data["error_message"],
            file_path=data.get("file_path"),
            line_number=data.get("line_number"),
            column_number=data.get("column_number"),
            context=data.get("context"),
            timestamp=data.get("timestamp")
        )
        
        instance.matched_patterns = data.get("matched_patterns", [])
        
        return instance


class ErrorCollector:
    """Collects and analyzes errors."""
    
    def __init__(self, project_path: str):
        """Initialize error collector.
        
        Args:
            project_path: Path to the project directory.
        """
        self.project_path = Path(project_path)
        self.error_patterns = {}  # type: Dict[str, ErrorPattern]
        self.error_instances = {}  # type: Dict[str, ErrorInstance]
        
        # Load built-in error patterns
        self._load_built_in_patterns()
    
    def _load_built_in_patterns(self):
        """Load built-in error patterns."""
        # Python syntax errors
        self.add_error_pattern(
            pattern=r"SyntaxError: invalid syntax",
            description="Invalid syntax in Python code",
            examples=["SyntaxError: invalid syntax"],
            fix_suggestions=[
                "Check for missing parentheses, brackets, or quotes",
                "Ensure proper indentation",
                "Check for missing colons after if/for/while statements"
            ]
        )
        
        self.add_error_pattern(
            pattern=r"IndentationError: (expected an indented block|unexpected indent)",
            description="Indentation error in Python code",
            examples=[
                "IndentationError: expected an indented block",
                "IndentationError: unexpected indent"
            ],
            fix_suggestions=[
                "Ensure consistent indentation (use either tabs or spaces, not both)",
                "Check for missing indentation after if/for/while statements",
                "Ensure all lines in a block have the same indentation level"
            ]
        )
        
        self.add_error_pattern(
            pattern=r"NameError: name '(\w+)' is not defined",
            description="Reference to undefined variable in Python code",
            examples=["NameError: name 'foo' is not defined"],
            fix_suggestions=[
                "Check for typos in variable names",
                "Ensure the variable is defined before it is used",
                "Check if the variable is defined in the correct scope"
            ]
        )
        
        # JavaScript syntax errors
        self.add_error_pattern(
            pattern=r"SyntaxError: Unexpected token",
            description="Unexpected token in JavaScript code",
            examples=["SyntaxError: Unexpected token ')'"],
            fix_suggestions=[
                "Check for missing or mismatched parentheses, brackets, or braces",
                "Ensure proper semicolon usage",
                "Check for invalid JavaScript syntax"
            ]
        )
        
        self.add_error_pattern(
            pattern=r"ReferenceError: (\w+) is not defined",
            description="Reference to undefined variable in JavaScript code",
            examples=["ReferenceError: foo is not defined"],
            fix_suggestions=[
                "Check for typos in variable names",
                "Ensure the variable is defined before it is used",
                "Check if the variable is defined in the correct scope"
            ]
        )
        
        # Import errors
        self.add_error_pattern(
            pattern=r"ImportError: No module named '(\w+)'",
            description="Module import error in Python code",
            examples=["ImportError: No module named 'requests'"],
            fix_suggestions=[
                "Install the missing module using pip",
                "Check for typos in the module name",
                "Ensure the module is in the Python path"
            ]
        )
        
        self.add_error_pattern(
            pattern=r"ModuleNotFoundError: No module named '(\w+)'",
            description="Module not found error in Python code",
            examples=["ModuleNotFoundError: No module named 'requests'"],
            fix_suggestions=[
                "Install the missing module using pip",
                "Check for typos in the module name",
                "Ensure the module is in the Python path"
            ]
        )
        
        # Type errors
        self.add_error_pattern(
            pattern=r"TypeError: (.*)",
            description="Type error in Python code",
            examples=[
                "TypeError: can't multiply sequence by non-int of type 'str'",
                "TypeError: 'int' object is not iterable"
            ],
            fix_suggestions=[
                "Check the types of the variables involved",
                "Ensure proper type conversion where needed",
                "Use appropriate methods for the data types"
            ]
        )
    
    def add_error_pattern(self, pattern: str, description: str, 
                        examples: List[str] = None, fix_suggestions: List[str] = None) -> str:
        """Add an error pattern.
        
        Args:
            pattern: Regular expression pattern to match errors.
            description: Description of the error pattern.
            examples: Examples of errors that match the pattern.
            fix_suggestions: Suggestions for fixing the error.
            
        Returns:
            ID of the added pattern.
        """
        # Generate a unique ID for the pattern
        pattern_id = hashlib.md5(pattern.encode()).hexdigest()[:8]
        
        # Create the pattern
        error_pattern = ErrorPattern(
            pattern_id=pattern_id,
            pattern=pattern,
            description=description,
            examples=examples,
            fix_suggestions=fix_suggestions
        )
        
        # Add the pattern
        self.error_patterns[pattern_id] = error_pattern
        
        return pattern_id
    
    def add_error(self, error_message: str, file_path: str = None, 
                line_number: int = None, column_number: int = None, 
                context: str = None, timestamp: float = None) -> str:
        """Add an error.
        
        Args:
            error_message: Error message.
            file_path: Path to the file where the error occurred.
            line_number: Line number where the error occurred.
            column_number: Column number where the error occurred.
            context: Context of the error (e.g., surrounding code).
            timestamp: Timestamp of when the error occurred.
            
        Returns:
            ID of the added error.
        """
        import time
        
        # Generate a unique ID for the error
        error_id = hashlib.md5(f"{error_message}:{file_path}:{line_number}:{column_number}".encode()).hexdigest()[:8]
        
        # Create the error instance
        error_instance = ErrorInstance(
            error_id=error_id,
            error_message=error_message,
            file_path=file_path,
            line_number=line_number,
            column_number=column_number,
            context=context,
            timestamp=timestamp or time.time()
        )
        
        # Match against patterns
        for pattern_id, pattern in self.error_patterns.items():
            if pattern.matches(error_message):
                error_instance.add_matched_pattern(pattern_id)
        
        # Add the error
        self.error_instances[error_id] = error_instance
        
        return error_id
    
    def get_error(self, error_id: str) -> Optional[ErrorInstance]:
        """Get an error by ID.
        
        Args:
            error_id: ID of the error.
            
        Returns:
            Error instance or None if not found.
        """
        return self.error_instances.get(error_id)
    
    def get_pattern(self, pattern_id: str) -> Optional[ErrorPattern]:
        """Get a pattern by ID.
        
        Args:
            pattern_id: ID of the pattern.
            
        Returns:
            Error pattern or None if not found.
        """
        return self.error_patterns.get(pattern_id)
    
    def get_fix_suggestions(self, error_id: str) -> List[str]:
        """Get fix suggestions for an error.
        
        Args:
            error_id: ID of the error.
            
        Returns:
            List of fix suggestions.
        """
        error = self.get_error(error_id)
        if not error:
            return []
        
        suggestions = []
        for pattern_id in error.matched_patterns:
            pattern = self.get_pattern(pattern_id)
            if pattern:
                suggestions.extend(pattern.fix_suggestions)
        
        return suggestions
    
    def get_errors_by_pattern(self, pattern_id: str) -> List[ErrorInstance]:
        """Get errors that match a pattern.
        
        Args:
            pattern_id: ID of the pattern.
            
        Returns:
            List of error instances.
        """
        return [
            error for error in self.error_instances.values()
            if pattern_id in error.matched_patterns
        ]
    
    def get_errors_by_file(self, file_path: str) -> List[ErrorInstance]:
        """Get errors that occurred in a file.
        
        Args:
            file_path: Path to the file.
            
        Returns:
            List of error instances.
        """
        return [
            error for error in self.error_instances.values()
            if error.file_path == file_path
        ]
    
    def get_most_common_patterns(self, limit: int = 5) -> List[Tuple[str, int]]:
        """Get the most common error patterns.
        
        Args:
            limit: Maximum number of patterns to return.
            
        Returns:
            List of (pattern_id, count) tuples.
        """
        pattern_counts = {}  # type: Dict[str, int]
        
        for error in self.error_instances.values():
            for pattern_id in error.matched_patterns:
                pattern_counts[pattern_id] = pattern_counts.get(pattern_id, 0) + 1
        
        return sorted(pattern_counts.items(), key=lambda x: x[1], reverse=True)[:limit]
    
    def generate_error_report(self) -> Table:
        """Generate a report of errors.
        
        Returns:
            Rich Table object.
        """
        table = Table(title="Error Report")
        
        table.add_column("Error ID", style="cyan")
        table.add_column("Error Message", style="red")
        table.add_column("File", style="green")
        table.add_column("Line", style="yellow")
        table.add_column("Patterns", style="magenta")
        
        for error_id, error in self.error_instances.items():
            patterns = ", ".join(error.matched_patterns)
            
            table.add_row(
                error_id,
                error.error_message[:50] + "..." if len(error.error_message) > 50 else error.error_message,
                error.file_path or "N/A",
                str(error.line_number) if error.line_number else "N/A",
                patterns or "No patterns matched"
            )
        
        return table
    
    def save_to_file(self, file_path: str) -> bool:
        """Save error data to a file.
        
        Args:
            file_path: Path to save the data to.
            
        Returns:
            Whether the save was successful.
        """
        try:
            data = {
                "patterns": {pattern_id: pattern.to_dict() for pattern_id, pattern in self.error_patterns.items()},
                "errors": {error_id: error.to_dict() for error_id, error in self.error_instances.items()}
            }
            
            with open(file_path, 'w') as f:
                json.dump(data, f, indent=2)
            
            console.print(f"[green]Error data saved to {file_path}[/green]")
            return True
        except Exception as e:
            console.print(f"[red]Error saving error data: {str(e)}[/red]")
            return False
    
    def load_from_file(self, file_path: str) -> bool:
        """Load error data from a file.
        
        Args:
            file_path: Path to load the data from.
            
        Returns:
            Whether the load was successful.
        """
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
            
            self.error_patterns = {
                pattern_id: ErrorPattern.from_dict(pattern_data)
                for pattern_id, pattern_data in data.get("patterns", {}).items()
            }
            
            self.error_instances = {
                error_id: ErrorInstance.from_dict(error_data)
                for error_id, error_data in data.get("errors", {}).items()
            }
            
            console.print(f"[green]Error data loaded from {file_path}[/green]")
            return True
        except Exception as e:
            console.print(f"[red]Error loading error data: {str(e)}[/red]")
            return False
