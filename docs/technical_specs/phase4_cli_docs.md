# Technical Specification: Phase 4 - CLI Integration and Documentation

## Overview

This document provides detailed technical specifications for implementing the CLI integration and documentation in Phase 4 of the codebase analyzer enhancement project. This phase focuses on making all the new functions accessible through the command-line interface and ensuring comprehensive documentation for users.

## 1. CLI Argument Integration

### Purpose
To integrate all new functions with the CLI interface, making them easily accessible to users through the command line.

### CLI Architecture

The CLI integration will follow a modular architecture with the following components:

1. **Command Parser**: Parses command-line arguments and validates input
2. **Command Executor**: Executes the appropriate function based on the command
3. **Output Formatter**: Formats the output for display to the user
4. **Error Handler**: Handles errors and provides informative messages

### Command Structure

The CLI commands will be structured as follows:

```
projects analyze_codebase [options]
```

Where `[options]` can include:

- General options (e.g., `--project-path`, `--output-file`)
- Analysis options (e.g., `--analyze-call-chains`, `--detect-dead-code`)
- Visualization options (e.g., `--visualize-module-dependencies`, `--visualize-blast-radius`)
- Utility options (e.g., `--find-paths`, `--break-circular-dependencies`)

### Command Groups

Commands will be organized into logical groups:

1. **Analysis Commands**: Functions for analyzing code structure and relationships
2. **Visualization Commands**: Functions for visualizing code structure and relationships
3. **Utility Commands**: Functions for performing various code-related tasks
4. **Configuration Commands**: Functions for configuring the analyzer

### Implementation Details

```python
def setup_cli_parser():
    """Set up the command-line argument parser.
    
    Returns:
        ArgumentParser instance.
    """
    parser = argparse.ArgumentParser(description='Analyze a codebase and extract insights.')
    
    # General options
    parser.add_argument('--project-path', default='.',
                        help='Path to the project directory')
    parser.add_argument('--output-file',
                        help='Path to save the analysis results')
    parser.add_argument('--verbose', action='store_true',
                        help='Enable verbose output')
    
    # Create subparsers for command groups
    subparsers = parser.add_subparsers(dest='command', help='Command to execute')
    
    # Analysis commands
    analysis_parser = subparsers.add_parser('analyze', help='Analyze the codebase')
    setup_analysis_parser(analysis_parser)
    
    # Visualization commands
    visualization_parser = subparsers.add_parser('visualize', help='Visualize the codebase')
    setup_visualization_parser(visualization_parser)
    
    # Utility commands
    utility_parser = subparsers.add_parser('utility', help='Perform utility tasks')
    setup_utility_parser(utility_parser)
    
    # Configuration commands
    config_parser = subparsers.add_parser('config', help='Configure the analyzer')
    setup_config_parser(config_parser)
    
    return parser

def setup_analysis_parser(parser):
    """Set up the analysis command parser.
    
    Args:
        parser: ArgumentParser instance.
    """
    # Add analysis options
    parser.add_argument('--analyze-call-chains', action='store_true',
                        help='Analyze call chains between functions')
    parser.add_argument('--max-chain-depth', type=int, default=None,
                        help='Maximum depth of call chains to analyze')
    # Add more analysis options...

def setup_visualization_parser(parser):
    """Set up the visualization command parser.
    
    Args:
        parser: ArgumentParser instance.
    """
    # Add visualization options
    parser.add_argument('--visualize-module-dependencies', action='store_true',
                        help='Visualize dependencies between modules')
    parser.add_argument('--output-format', choices=['html', 'png', 'svg'], default='html',
                        help='Output format for visualizations')
    # Add more visualization options...

def setup_utility_parser(parser):
    """Set up the utility command parser.
    
    Args:
        parser: ArgumentParser instance.
    """
    # Add utility options
    parser.add_argument('--find-paths', action='store_true',
                        help='Find all possible paths between two functions')
    parser.add_argument('--source-function',
                        help='ID of the source function')
    # Add more utility options...

def setup_config_parser(parser):
    """Set up the configuration command parser.
    
    Args:
        parser: ArgumentParser instance.
    """
    # Add configuration options
    parser.add_argument('--set', nargs=2, metavar=('KEY', 'VALUE'), action='append',
                        help='Set a configuration value')
    parser.add_argument('--show', action='store_true',
                        help='Show current configuration')
    # Add more configuration options...

def main():
    """Main entry point for the CLI."""
    parser = setup_cli_parser()
    args = parser.parse_args()
    
    # Execute the appropriate command
    if args.command == 'analyze':
        execute_analysis_command(args)
    elif args.command == 'visualize':
        execute_visualization_command(args)
    elif args.command == 'utility':
        execute_utility_command(args)
    elif args.command == 'config':
        execute_config_command(args)
    else:
        # Default to analyzing the codebase
        analyzer = CodebaseAnalyzer(args.project_path)
        results = analyzer.analyze_codebase()
        
        if args.output_file:
            analyzer.export_analysis(args.output_file)
        else:
            # Print summary to console
            print_analysis_summary(results)

def execute_analysis_command(args):
    """Execute an analysis command.
    
    Args:
        args: Parsed command-line arguments.
    """
    analyzer = CodebaseAnalyzer(args.project_path)
    
    if args.analyze_call_chains:
        results = analyzer.analyze_call_chains(max_depth=args.max_chain_depth)
        print_analysis_results(results)
    # Handle other analysis commands...

def execute_visualization_command(args):
    """Execute a visualization command.
    
    Args:
        args: Parsed command-line arguments.
    """
    analyzer = CodebaseAnalyzer(args.project_path)
    
    if args.visualize_module_dependencies:
        results = analyzer.visualize_module_dependencies(output_format=args.output_format)
        print_visualization_results(results)
    # Handle other visualization commands...

def execute_utility_command(args):
    """Execute a utility command.
    
    Args:
        args: Parsed command-line arguments.
    """
    analyzer = CodebaseAnalyzer(args.project_path)
    
    if args.find_paths:
        if not args.source_function or not args.target_function:
            print("Error: --source-function and --target-function are required for --find-paths")
            return
        
        results = analyzer.find_all_paths(args.source_function, args.target_function,
                                         max_paths=args.max_paths)
        print_utility_results(results)
    # Handle other utility commands...

def execute_config_command(args):
    """Execute a configuration command.
    
    Args:
        args: Parsed command-line arguments.
    """
    if args.show:
        show_configuration()
    elif args.set:
        for key, value in args.set:
            set_configuration(key, value)
    # Handle other configuration commands...

def print_analysis_summary(results):
    """Print a summary of analysis results.
    
    Args:
        results: Analysis results.
    """
    # Implementation details...

def print_analysis_results(results):
    """Print analysis results.
    
    Args:
        results: Analysis results.
    """
    # Implementation details...

def print_visualization_results(results):
    """Print visualization results.
    
    Args:
        results: Visualization results.
    """
    # Implementation details...

def print_utility_results(results):
    """Print utility results.
    
    Args:
        results: Utility results.
    """
    # Implementation details...

def show_configuration():
    """Show current configuration."""
    # Implementation details...

def set_configuration(key, value):
    """Set a configuration value.
    
    Args:
        key: Configuration key.
        value: Configuration value.
    """
    # Implementation details...
```

## 2. Documentation Updates

### Purpose
To update documentation to reflect the new capabilities, helping users understand and use the enhanced codebase analyzer effectively.

### Documentation Structure

The documentation will be organized into the following sections:

1. **Overview**: Introduction to the codebase analyzer and its capabilities
2. **Installation**: Instructions for installing the tool
3. **Usage**: General usage instructions and examples
4. **Commands**: Detailed documentation for each command
5. **Configuration**: Information about configuring the tool
6. **Examples**: Real-world examples of using the tool
7. **API Reference**: Reference documentation for the Python API
8. **Contributing**: Guidelines for contributing to the project

### Docstring Updates

All new functions will have comprehensive docstrings following the Google style guide:

```python
def analyze_call_chains(self, max_depth: int = None, include_patterns: List[str] = None, 
                        exclude_patterns: List[str] = None) -> Dict[str, Any]:
    """Analyze call chains in the codebase.
    
    This function analyzes the call chains between functions in the codebase,
    helping developers understand the flow of execution and dependencies
    between functions.
    
    Args:
        max_depth: Maximum depth of call chains to analyze. If None, no limit is applied.
        include_patterns: List of glob patterns to include. If None, all files are included.
        exclude_patterns: List of glob patterns to exclude. If None, no files are excluded.
        
    Returns:
        Dictionary with call chain analysis results, containing:
        - 'call_graph': Dictionary representation of the call graph
        - 'max_chain_length': Length of the longest call chain
        - 'max_chain': List of function IDs in the longest call chain
        - 'summary': Summary of the analysis results
        
    Examples:
        >>> analyzer = CodebaseAnalyzer('path/to/project')
        >>> results = analyzer.analyze_call_chains(max_depth=5)
        >>> print(f"Longest call chain: {results['max_chain_length']}")
        Longest call chain: 7
    """
    # Implementation...
```

### README Updates

The README.md file will be updated to include information about the new capabilities:

```markdown
# Projects Tools

A command line tool for managing projects with LLM integration.

## Features

- **Project Creation**: Create Python backend and frontend (React/Vue) projects
- **LLM Integration**: Generate code, analyze codebases, and debug components using LLMs
- **Project Analysis**: Analyze codebases and generate insights
  - Call Chain Analysis
  - Dead Code Detection
  - Type Coverage Analysis
  - Module Coupling Analysis
- **Codebase Visualization**: Visualize code structure and relationships
  - Module Dependency Visualization
  - Inheritance Graph Visualization
  - React Component Tree Visualization
  - HTTP Method Visualization
- **Utility Functions**: Perform various code-related tasks
  - Find Paths Between Functions
  - Break Circular Dependencies
  - Calculate Type Coverage Percentages
  - Analyze Module Coupling
- **Configuration Management**: Centralized configuration system
- **Error Handling**: Comprehensive error handling and validation
- **Template System**: Flexible templating for project generation

## Installation

```bash
pip install projects-tools
```

## Usage

### Analyze a codebase

```bash
# Analyze call chains
projects analyze --analyze-call-chains --max-chain-depth 5

# Detect dead code
projects analyze --detect-dead-code --exclude-patterns "test_*.py" "**/__pycache__/**"

# Analyze type coverage
projects analyze --analyze-type-coverage --coverage-threshold 0.8
```

### Visualize a codebase

```bash
# Visualize module dependencies
projects visualize --visualize-module-dependencies --output-format html

# Visualize blast radius
projects visualize --visualize-blast-radius "my_module.my_function" --impact-depth 3

# Visualize inheritance graph
projects visualize --visualize-inheritance --base-class "BaseClass"
```

### Perform utility tasks

```bash
# Find paths between functions
projects utility --find-paths --source-function "module1.func1" --target-function "module2.func2"

# Break circular dependencies
projects utility --break-circular-dependencies --resolution-strategy extract

# Calculate type coverage percentages
projects utility --calculate-type-coverage --coverage-level project --output-format json
```

### Configure the tool

```bash
# Show current configuration
projects config --show

# Set configuration values
projects config --set llm.default_provider anthropic

# Save configuration
projects config --save
```

## Documentation

For detailed documentation, see the [User Guide](docs/user_guide.md).
```

### User Guide

A comprehensive user guide will be created with detailed information about each function:

```markdown
# User Guide

## Table of Contents

1. [Introduction](#introduction)
2. [Installation](#installation)
3. [Basic Usage](#basic-usage)
4. [Analysis Commands](#analysis-commands)
   - [Call Chain Analysis](#call-chain-analysis)
   - [Dead Code Detection](#dead-code-detection)
   - [Type Resolution](#type-resolution)
   - [Type Coverage Analysis](#type-coverage-analysis)
   - [Other Analysis Commands](#other-analysis-commands)
5. [Visualization Commands](#visualization-commands)
   - [Module Dependency Visualization](#module-dependency-visualization)
   - [Blast Radius Visualization](#blast-radius-visualization)
   - [Inheritance Graph Visualization](#inheritance-graph-visualization)
   - [Usage Relationship Visualization](#usage-relationship-visualization)
   - [React Component Tree Visualization](#react-component-tree-visualization)
   - [HTTP Method Visualization](#http-method-visualization)
6. [Utility Commands](#utility-commands)
   - [Find Paths Between Functions](#find-paths-between-functions)
   - [Break Circular Dependencies](#break-circular-dependencies)
   - [Calculate Type Coverage Percentages](#calculate-type-coverage-percentages)
   - [Analyze Module Coupling](#analyze-module-coupling)
   - [Other Utility Commands](#other-utility-commands)
7. [Configuration](#configuration)
8. [Advanced Usage](#advanced-usage)
9. [Troubleshooting](#troubleshooting)
10. [API Reference](#api-reference)

## Introduction

The Projects Tools codebase analyzer is a powerful tool for analyzing and visualizing codebases. It provides a wide range of functions for understanding code structure, dependencies, and quality.

## Installation

...

## Basic Usage

...

## Analysis Commands

### Call Chain Analysis

The call chain analysis function helps you understand the flow of execution and dependencies between functions in your codebase.

#### Command

```bash
projects analyze --analyze-call-chains [options]
```

#### Options

- `--max-chain-depth`: Maximum depth of call chains to analyze
- `--include-patterns`: Glob patterns to include in the analysis
- `--exclude-patterns`: Glob patterns to exclude from the analysis

#### Example

```bash
projects analyze --analyze-call-chains --max-chain-depth 5
```

#### Output

The command outputs a summary of the call chain analysis, including:

- The longest call chain in the codebase
- Functions with the most callers
- Functions with the most callees
- Potential performance bottlenecks

If you specify an output file with `--output-file`, the full analysis results will be saved to that file.

...
```

### API Reference

A comprehensive API reference will be generated using Sphinx:

```python
# conf.py
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',
    'sphinx.ext.viewcode',
]

# index.rst
.. Projects Tools documentation master file

Welcome to Projects Tools's documentation!
=========================================

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   installation
   usage
   api
   contributing

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

# api.rst
API Reference
============

CodebaseAnalyzer
---------------

.. autoclass:: projects_tools.llm_integration.codebase_analyzer.CodebaseAnalyzer
   :members:
   :undoc-members:
   :show-inheritance:

DependencyGraph
--------------

.. autoclass:: projects_tools.llm_integration.codebase_analyzer.DependencyGraph
   :members:
   :undoc-members:
   :show-inheritance:

...
```

## 3. Testing

### Purpose
To ensure that all new functions work correctly and reliably, helping developers maintain code quality and prevent regressions.

### Test Structure

The tests will be organized into the following categories:

1. **Unit Tests**: Tests for individual components and functions
2. **Integration Tests**: Tests for end-to-end functionality
3. **Functional Tests**: Tests for specific use cases
4. **Performance Tests**: Tests for performance with large codebases

### Test Implementation

```python
# test_codebase_analyzer.py

import unittest
from unittest.mock import patch, MagicMock
import tempfile
import os
import json

from projects_tools.llm_integration.codebase_analyzer import CodebaseAnalyzer, DependencyGraph

class TestCodebaseAnalyzer(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.project_path = self.temp_dir.name
        
        # Create test files
        self._create_test_files()
        
        # Initialize analyzer
        self.analyzer = CodebaseAnalyzer(self.project_path)
    
    def tearDown(self):
        """Tear down test fixtures."""
        self.temp_dir.cleanup()
    
    def _create_test_files(self):
        """Create test files for analysis."""
        # Create a simple Python module
        module_a = """
def func_a():
    return func_b() + func_c()

def func_b():
    return 1

def func_c():
    return func_d()

def func_d():
    return 2
"""
        with open(os.path.join(self.project_path, 'module_a.py'), 'w') as f:
            f.write(module_a)
        
        # Create another Python module
        module_b = """
from module_a import func_a, func_b

def func_e():
    return func_a() + 3

def func_f():
    return func_b() + func_g()

def func_g():
    return 4
"""
        with open(os.path.join(self.project_path, 'module_b.py'), 'w') as f:
            f.write(module_b)
    
    def test_analyze_codebase(self):
        """Test basic codebase analysis."""
        results = self.analyzer.analyze_codebase()
        
        # Check that the analysis results contain the expected keys
        self.assertIn('dependency_graph', results)
        self.assertIn('code_metrics', results)
        self.assertIn('summary', results)
        
        # Check that the dependency graph contains the expected nodes
        dependency_graph = results['dependency_graph']
        self.assertIn('nodes', dependency_graph)
        
        # Check that the code metrics contain the expected files
        code_metrics = results['code_metrics']
        self.assertIn('module_a.py', code_metrics)
        self.assertIn('module_b.py', code_metrics)
    
    def test_analyze_call_chains(self):
        """Test call chain analysis."""
        results = self.analyzer.analyze_call_chains()
        
        # Check that the analysis results contain the expected keys
        self.assertIn('call_graph', results)
        self.assertIn('max_chain_length', results)
        self.assertIn('max_chain', results)
        
        # Check that the max chain length is correct
        self.assertEqual(results['max_chain_length'], 3)
        
        # Check that the max chain contains the expected functions
        max_chain = results['max_chain']
        self.assertIn('module_b.func_e', max_chain)
        self.assertIn('module_a.func_a', max_chain)
        self.assertIn('module_a.func_c', max_chain)
        self.assertIn('module_a.func_d', max_chain)
    
    def test_detect_dead_code(self):
        """Test dead code detection."""
        # Create a file with dead code
        module_c = """
def used_func():
    return 1

def unused_func():
    return 2

class UsedClass:
    def method(self):
        return used_func()

class UnusedClass:
    def method(self):
        return unused_func()
"""
        with open(os.path.join(self.project_path, 'module_c.py'), 'w') as f:
            f.write(module_c)
        
        # Create a file that uses some of the code
        module_d = """
from module_c import used_func, UsedClass

def main():
    obj = UsedClass()
    return obj.method() + used_func()
"""
        with open(os.path.join(self.project_path, 'module_d.py'), 'w') as f:
            f.write(module_d)
        
        # Reinitialize analyzer to include the new files
        self.analyzer = CodebaseAnalyzer(self.project_path)
        
        results = self.analyzer.detect_dead_code()
        
        # Check that the analysis results contain the expected keys
        self.assertIn('unused_symbols', results)
        self.assertIn('unused_files', results)
        
        # Check that the unused symbols include the expected symbols
        unused_symbols = results['unused_symbols']
        self.assertIn('module_c.py', unused_symbols)
        self.assertIn('unused_func', unused_symbols['module_c.py'])
        self.assertIn('UnusedClass', unused_symbols['module_c.py'])
    
    # Add more tests for other functions...

class TestDependencyGraph(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures."""
        self.graph = DependencyGraph()
        
        # Add some nodes and edges
        self.graph.add_node('A')
        self.graph.add_node('B')
        self.graph.add_node('C')
        self.graph.add_edge('A', 'B')
        self.graph.add_edge('B', 'C')
        self.graph.add_edge('A', 'C')
    
    def test_get_dependencies(self):
        """Test getting dependencies of a node."""
        deps = self.graph.get_dependencies('A')
        self.assertEqual(deps, {'B', 'C'})
        
        deps = self.graph.get_dependencies('B')
        self.assertEqual(deps, {'C'})
        
        deps = self.graph.get_dependencies('C')
        self.assertEqual(deps, set())
    
    def test_get_dependents(self):
        """Test getting dependents of a node."""
        deps = self.graph.get_dependents('A')
        self.assertEqual(deps, set())
        
        deps = self.graph.get_dependents('B')
        self.assertEqual(deps, {'A'})
        
        deps = self.graph.get_dependents('C')
        self.assertEqual(deps, {'A', 'B'})
    
    def test_to_dict(self):
        """Test converting the graph to a dictionary."""
        graph_dict = self.graph.to_dict()
        
        self.assertIn('nodes', graph_dict)
        self.assertIn('metadata', graph_dict)
        
        nodes = graph_dict['nodes']
        self.assertEqual(nodes['A'], ['B', 'C'])
        self.assertEqual(nodes['B'], ['C'])
        self.assertEqual(nodes['C'], [])
    
    def test_from_dict(self):
        """Test creating a graph from a dictionary."""
        graph_dict = {
            'nodes': {
                'X': ['Y', 'Z'],
                'Y': ['Z'],
                'Z': []
            },
            'metadata': {}
        }
        
        graph = DependencyGraph.from_dict(graph_dict)
        
        self.assertEqual(graph.get_dependencies('X'), {'Y', 'Z'})
        self.assertEqual(graph.get_dependencies('Y'), {'Z'})
        self.assertEqual(graph.get_dependencies('Z'), set())
    
    # Add more tests for other methods...

# Add more test classes for other components...
```

### Test Coverage

Test coverage will be measured using the `coverage` tool:

```bash
coverage run -m unittest discover
coverage report -m
coverage html
```

## Integration with Existing Code

The CLI integration and documentation will be integrated with the existing codebase, following the same patterns and conventions. The implementation will leverage the existing CLI framework and documentation tools.

## Error Handling

The CLI integration will include comprehensive error handling:

1. Input validation to check for invalid arguments
2. Informative error messages for missing or invalid arguments
3. Graceful handling of exceptions during execution
4. Appropriate exit codes for different error conditions

## Documentation Tools

The documentation will be generated using the following tools:

1. **Sphinx**: For generating API reference documentation
2. **Markdown**: For user guides and examples
3. **Docstrings**: For inline documentation
4. **README**: For high-level overview and quick start

## Success Criteria

The CLI integration and documentation will be considered successful if:

1. All new functions are accessible through the CLI
2. The CLI provides appropriate help text and error messages
3. The documentation is comprehensive and up-to-date
4. The tests provide good coverage of the codebase
5. Users can easily understand and use the new functions

