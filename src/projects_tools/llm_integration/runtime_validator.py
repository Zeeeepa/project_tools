"""
Runtime Validator module for LLM integration.

This module provides functionality to validate code at runtime.
"""

import os
import sys
import ast
import json
import tempfile
import subprocess
import importlib.util
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path
from rich.console import Console
from rich.panel import Panel

from .validator import ValidationResult

console = Console()

class RuntimeValidationResult(ValidationResult):
    """Result of a runtime validation."""
    
    def __init__(self, success: bool, errors: List[str] = None, warnings: List[str] = None, 
                output: str = None, execution_time: float = None):
        """Initialize runtime validation result.
        
        Args:
            success: Whether the validation was successful.
            errors: List of error messages.
            warnings: List of warning messages.
            output: Output of the execution.
            execution_time: Execution time in seconds.
        """
        super().__init__(success, errors, warnings)
        self.output = output or ""
        self.execution_time = execution_time or 0.0
    
    def __str__(self):
        """Convert to string."""
        result = super().__str__()
        
        if self.output:
            result += f"\nOutput:\n{self.output}"
        
        if self.execution_time:
            result += f"\nExecution time: {self.execution_time:.2f}s"
        
        return result


class RuntimeValidator:
    """Validates code at runtime."""
    
    def __init__(self, project_path: str, timeout: int = 10):
        """Initialize runtime validator.
        
        Args:
            project_path: Path to the project directory.
            timeout: Timeout for code execution in seconds.
        """
        self.project_path = Path(project_path)
        self.timeout = timeout
    
    def validate_python_file(self, file_path: str, args: List[str] = None) -> RuntimeValidationResult:
        """Validate a Python file by executing it.
        
        Args:
            file_path: Path to the file to validate.
            args: Command-line arguments to pass to the script.
            
        Returns:
            Runtime validation result.
        """
        full_path = os.path.join(self.project_path, file_path)
        
        if not os.path.exists(full_path):
            return RuntimeValidationResult(False, errors=[f"File not found: {file_path}"])
        
        # Create a temporary directory for execution
        with tempfile.TemporaryDirectory() as temp_dir:
            # Copy the file to the temporary directory
            temp_file = os.path.join(temp_dir, os.path.basename(file_path))
            
            try:
                with open(full_path, 'r') as src_file:
                    content = src_file.read()
                
                with open(temp_file, 'w') as dst_file:
                    dst_file.write(content)
                
                # Execute the file in a subprocess
                cmd = [sys.executable, temp_file]
                if args:
                    cmd.extend(args)
                
                import time
                start_time = time.time()
                
                process = subprocess.run(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    timeout=self.timeout,
                    cwd=temp_dir
                )
                
                execution_time = time.time() - start_time
                
                # Check for errors
                if process.returncode != 0:
                    return RuntimeValidationResult(
                        False,
                        errors=[f"Execution failed with return code {process.returncode}", process.stderr],
                        output=process.stdout,
                        execution_time=execution_time
                    )
                
                # Check for warnings in stderr
                warnings = []
                if process.stderr:
                    warnings.append(process.stderr)
                
                return RuntimeValidationResult(
                    True,
                    warnings=warnings,
                    output=process.stdout,
                    execution_time=execution_time
                )
            
            except subprocess.TimeoutExpired:
                return RuntimeValidationResult(
                    False,
                    errors=[f"Execution timed out after {self.timeout} seconds"],
                    execution_time=self.timeout
                )
            except Exception as e:
                return RuntimeValidationResult(
                    False,
                    errors=[f"Error executing file: {str(e)}"]
                )
    
    def validate_python_function(self, file_path: str, function_name: str, 
                               args: List[Any] = None, kwargs: Dict[str, Any] = None) -> RuntimeValidationResult:
        """Validate a Python function by executing it.
        
        Args:
            file_path: Path to the file containing the function.
            function_name: Name of the function to validate.
            args: Positional arguments to pass to the function.
            kwargs: Keyword arguments to pass to the function.
            
        Returns:
            Runtime validation result.
        """
        full_path = os.path.join(self.project_path, file_path)
        
        if not os.path.exists(full_path):
            return RuntimeValidationResult(False, errors=[f"File not found: {file_path}"])
        
        # Create a temporary directory for execution
        with tempfile.TemporaryDirectory() as temp_dir:
            # Copy the file to the temporary directory
            temp_file = os.path.join(temp_dir, os.path.basename(file_path))
            
            try:
                with open(full_path, 'r') as src_file:
                    content = src_file.read()
                
                with open(temp_file, 'w') as dst_file:
                    dst_file.write(content)
                
                # Create a wrapper script to call the function
                wrapper_file = os.path.join(temp_dir, "wrapper.py")
                
                with open(wrapper_file, 'w') as f:
                    f.write(f"""
import sys
import json
import traceback
from {os.path.splitext(os.path.basename(file_path))[0]} import {function_name}

try:
    args = json.loads(sys.argv[1]) if len(sys.argv) > 1 else []
    kwargs = json.loads(sys.argv[2]) if len(sys.argv) > 2 else {{}}
    
    result = {function_name}(*args, **kwargs)
    
    print(json.dumps({{"success": True, "result": str(result)}}))
except Exception as e:
    traceback.print_exc()
    print(json.dumps({{"success": False, "error": str(e)}}))
""")
                
                # Execute the wrapper script
                args_json = json.dumps(args or [])
                kwargs_json = json.dumps(kwargs or {})
                
                import time
                start_time = time.time()
                
                process = subprocess.run(
                    [sys.executable, wrapper_file, args_json, kwargs_json],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    timeout=self.timeout,
                    cwd=temp_dir
                )
                
                execution_time = time.time() - start_time
                
                # Parse the output
                try:
                    output_lines = process.stdout.strip().split('\n')
                    result_json = json.loads(output_lines[-1])
                    
                    if result_json.get("success", False):
                        return RuntimeValidationResult(
                            True,
                            output=result_json.get("result", ""),
                            execution_time=execution_time
                        )
                    else:
                        return RuntimeValidationResult(
                            False,
                            errors=[result_json.get("error", "Unknown error")],
                            output='\n'.join(output_lines[:-1]),
                            execution_time=execution_time
                        )
                except json.JSONDecodeError:
                    # If the output is not valid JSON, return the raw output
                    return RuntimeValidationResult(
                        False,
                        errors=["Failed to parse function output"],
                        output=process.stdout,
                        execution_time=execution_time
                    )
            
            except subprocess.TimeoutExpired:
                return RuntimeValidationResult(
                    False,
                    errors=[f"Function execution timed out after {self.timeout} seconds"],
                    execution_time=self.timeout
                )
            except Exception as e:
                return RuntimeValidationResult(
                    False,
                    errors=[f"Error executing function: {str(e)}"]
                )
    
    def validate_javascript_file(self, file_path: str, args: List[str] = None) -> RuntimeValidationResult:
        """Validate a JavaScript file by executing it with Node.js.
        
        Args:
            file_path: Path to the file to validate.
            args: Command-line arguments to pass to the script.
            
        Returns:
            Runtime validation result.
        """
        full_path = os.path.join(self.project_path, file_path)
        
        if not os.path.exists(full_path):
            return RuntimeValidationResult(False, errors=[f"File not found: {file_path}"])
        
        # Check if Node.js is available
        try:
            subprocess.run(["node", "--version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        except FileNotFoundError:
            return RuntimeValidationResult(False, errors=["Node.js not found. Please install Node.js to validate JavaScript files."])
        
        # Create a temporary directory for execution
        with tempfile.TemporaryDirectory() as temp_dir:
            # Copy the file to the temporary directory
            temp_file = os.path.join(temp_dir, os.path.basename(file_path))
            
            try:
                with open(full_path, 'r') as src_file:
                    content = src_file.read()
                
                with open(temp_file, 'w') as dst_file:
                    dst_file.write(content)
                
                # Execute the file with Node.js
                cmd = ["node", temp_file]
                if args:
                    cmd.extend(args)
                
                import time
                start_time = time.time()
                
                process = subprocess.run(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    timeout=self.timeout,
                    cwd=temp_dir
                )
                
                execution_time = time.time() - start_time
                
                # Check for errors
                if process.returncode != 0:
                    return RuntimeValidationResult(
                        False,
                        errors=[f"Execution failed with return code {process.returncode}", process.stderr],
                        output=process.stdout,
                        execution_time=execution_time
                    )
                
                # Check for warnings in stderr
                warnings = []
                if process.stderr:
                    warnings.append(process.stderr)
                
                return RuntimeValidationResult(
                    True,
                    warnings=warnings,
                    output=process.stdout,
                    execution_time=execution_time
                )
            
            except subprocess.TimeoutExpired:
                return RuntimeValidationResult(
                    False,
                    errors=[f"Execution timed out after {self.timeout} seconds"],
                    execution_time=self.timeout
                )
            except Exception as e:
                return RuntimeValidationResult(
                    False,
                    errors=[f"Error executing file: {str(e)}"]
                )
    
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
        full_path = os.path.join(self.project_path, file_path)
        
        if not os.path.exists(full_path):
            return RuntimeValidationResult(False, errors=[f"File not found: {file_path}"])
        
        # Create a temporary directory for execution
        with tempfile.TemporaryDirectory() as temp_dir:
            # Copy the file to the temporary directory
            temp_file = os.path.join(temp_dir, os.path.basename(file_path))
            
            try:
                with open(full_path, 'r') as src_file:
                    content = src_file.read()
                
                with open(temp_file, 'w') as dst_file:
                    dst_file.write(content)
                
                # Create a wrapper script to start the server and make a request
                wrapper_file = os.path.join(temp_dir, "wrapper.py")
                
                with open(wrapper_file, 'w') as f:
                    f.write(f"""
import sys
import json
import time
import subprocess
import requests
import threading
import traceback

def start_server():
    try:
        subprocess.run([sys.executable, "{os.path.basename(temp_file)}"], check=True)
    except Exception as e:
        print(f"Error starting server: {{e}}")

# Start the server in a separate thread
server_thread = threading.Thread(target=start_server)
server_thread.daemon = True
server_thread.start()

# Wait for the server to start
time.sleep(2)

try:
    # Make the request
    method = "{method}"
    url = "{endpoint}"
    data = {json.dumps(data or {})}
    headers = {json.dumps(headers or {})}
    
    response = requests.request(method, url, json=data, headers=headers, timeout={self.timeout})
    
    print(json.dumps({{
        "success": response.status_code < 400,
        "status_code": response.status_code,
        "headers": dict(response.headers),
        "body": response.text
    }}))
except Exception as e:
    traceback.print_exc()
    print(json.dumps({{
        "success": False,
        "error": str(e)
    }}))
""")
                
                # Install requests if not already installed
                subprocess.run([sys.executable, "-m", "pip", "install", "requests"], 
                              stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                
                # Execute the wrapper script
                import time
                start_time = time.time()
                
                process = subprocess.run(
                    [sys.executable, wrapper_file],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    timeout=self.timeout * 2,  # Double timeout to account for server startup
                    cwd=temp_dir
                )
                
                execution_time = time.time() - start_time
                
                # Parse the output
                try:
                    output_lines = process.stdout.strip().split('\n')
                    result_json = json.loads(output_lines[-1])
                    
                    if result_json.get("success", False):
                        return RuntimeValidationResult(
                            True,
                            output=f"Status: {result_json.get('status_code')}\nBody: {result_json.get('body')}",
                            execution_time=execution_time
                        )
                    else:
                        return RuntimeValidationResult(
                            False,
                            errors=[result_json.get("error", "Unknown error")],
                            output='\n'.join(output_lines[:-1]),
                            execution_time=execution_time
                        )
                except json.JSONDecodeError:
                    # If the output is not valid JSON, return the raw output
                    return RuntimeValidationResult(
                        False,
                        errors=["Failed to parse API response"],
                        output=process.stdout,
                        execution_time=execution_time
                    )
            
            except subprocess.TimeoutExpired:
                return RuntimeValidationResult(
                    False,
                    errors=[f"API request timed out after {self.timeout * 2} seconds"],
                    execution_time=self.timeout * 2
                )
            except Exception as e:
                return RuntimeValidationResult(
                    False,
                    errors=[f"Error validating API endpoint: {str(e)}"]
                )
