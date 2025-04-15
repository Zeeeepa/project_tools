"""
Code Validator module for LLM integration.

This module provides functionality to validate generated code.
"""

import os
import re
import subprocess
import tempfile
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path
from rich.console import Console
from rich.panel import Panel

console = Console()

class ValidationResult:
    """Result of a code validation."""
    
    def __init__(self, success: bool, errors: List[str] = None, warnings: List[str] = None):
        """Initialize validation result.
        
        Args:
            success: Whether the validation was successful.
            errors: List of error messages.
            warnings: List of warning messages.
        """
        self.success = success
        self.errors = errors or []
        self.warnings = warnings or []
    
    def __bool__(self):
        """Convert to boolean."""
        return self.success
    
    def __str__(self):
        """Convert to string."""
        if self.success:
            return "Validation successful"
        
        result = "Validation failed:\n"
        if self.errors:
            result += "Errors:\n" + "\n".join(f"- {e}" for e in self.errors) + "\n"
        if self.warnings:
            result += "Warnings:\n" + "\n".join(f"- {w}" for w in self.warnings)
        
        return result


class CodeValidator:
    """Validates generated code."""
    
    def __init__(self, project_path: str):
        """Initialize code validator.
        
        Args:
            project_path: Path to the project directory.
        """
        self.project_path = Path(project_path)
    
    def validate_file(self, file_path: str) -> ValidationResult:
        """Validate a file.
        
        Args:
            file_path: Path to the file to validate.
            
        Returns:
            Validation result.
        """
        full_path = os.path.join(self.project_path, file_path)
        
        if not os.path.exists(full_path):
            return ValidationResult(False, errors=[f"File not found: {file_path}"])
        
        # Determine file type
        file_ext = os.path.splitext(file_path)[1].lower()
        
        if file_ext in ['.py']:
            return self._validate_python(full_path)
        elif file_ext in ['.js', '.jsx', '.ts', '.tsx']:
            return self._validate_javascript(full_path)
        else:
            # For other file types, just check if it's a valid file
            return ValidationResult(True, warnings=[f"No specific validation for {file_ext} files"])
    
    def _validate_python(self, file_path: str) -> ValidationResult:
        """Validate a Python file.
        
        Args:
            file_path: Path to the file to validate.
            
        Returns:
            Validation result.
        """
        # Check syntax
        syntax_result = self._check_python_syntax(file_path)
        if not syntax_result.success:
            return syntax_result
        
        # If available, run pylint
        pylint_result = self._run_pylint(file_path)
        
        # Combine results
        success = syntax_result.success and (pylint_result.success if pylint_result else True)
        errors = syntax_result.errors + (pylint_result.errors if pylint_result else [])
        warnings = syntax_result.warnings + (pylint_result.warnings if pylint_result else [])
        
        return ValidationResult(success, errors, warnings)
    
    def _check_python_syntax(self, file_path: str) -> ValidationResult:
        """Check Python syntax.
        
        Args:
            file_path: Path to the file to check.
            
        Returns:
            Validation result.
        """
        try:
            with open(file_path, 'r') as f:
                source = f.read()
            
            # Try to compile the code to check for syntax errors
            compile(source, file_path, 'exec')
            return ValidationResult(True)
        except SyntaxError as e:
            return ValidationResult(False, errors=[f"Syntax error at line {e.lineno}: {e.msg}"])
        except Exception as e:
            return ValidationResult(False, errors=[f"Error checking syntax: {str(e)}"])
    
    def _run_pylint(self, file_path: str) -> Optional[ValidationResult]:
        """Run pylint on a Python file.
        
        Args:
            file_path: Path to the file to check.
            
        Returns:
            Validation result or None if pylint is not available.
        """
        try:
            # Check if pylint is available
            result = subprocess.run(['pylint', '--version'], 
                                   stdout=subprocess.PIPE, 
                                   stderr=subprocess.PIPE,
                                   text=True)
            
            if result.returncode != 0:
                return None
            
            # Run pylint
            result = subprocess.run(['pylint', '--output-format=text', file_path], 
                                   stdout=subprocess.PIPE, 
                                   stderr=subprocess.PIPE,
                                   text=True)
            
            # Parse output
            errors = []
            warnings = []
            
            for line in result.stdout.splitlines():
                if 'error' in line.lower():
                    errors.append(line)
                elif 'warning' in line.lower():
                    warnings.append(line)
            
            return ValidationResult(len(errors) == 0, errors, warnings)
        except Exception:
            # Pylint not available
            return None
    
    def _validate_javascript(self, file_path: str) -> ValidationResult:
        """Validate a JavaScript/TypeScript file.
        
        Args:
            file_path: Path to the file to validate.
            
        Returns:
            Validation result.
        """
        # If available, run eslint
        eslint_result = self._run_eslint(file_path)
        if eslint_result:
            return eslint_result
        
        # If eslint is not available, just check if it's a valid file
        try:
            with open(file_path, 'r') as f:
                f.read()
            return ValidationResult(True, warnings=["ESLint not available for detailed validation"])
        except Exception as e:
            return ValidationResult(False, errors=[f"Error reading file: {str(e)}"])
    
    def _run_eslint(self, file_path: str) -> Optional[ValidationResult]:
        """Run eslint on a JavaScript/TypeScript file.
        
        Args:
            file_path: Path to the file to check.
            
        Returns:
            Validation result or None if eslint is not available.
        """
        try:
            # Check if eslint is available
            result = subprocess.run(['eslint', '--version'], 
                                   stdout=subprocess.PIPE, 
                                   stderr=subprocess.PIPE,
                                   text=True)
            
            if result.returncode != 0:
                return None
            
            # Run eslint
            result = subprocess.run(['eslint', '--format=unix', file_path], 
                                   stdout=subprocess.PIPE, 
                                   stderr=subprocess.PIPE,
                                   text=True)
            
            # Parse output
            errors = []
            warnings = []
            
            for line in result.stdout.splitlines():
                if 'error' in line.lower():
                    errors.append(line)
                elif 'warning' in line.lower():
                    warnings.append(line)
            
            return ValidationResult(len(errors) == 0, errors, warnings)
        except Exception:
            # ESLint not available
            return None
