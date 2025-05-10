# Technical Specification: Phase 3 - Utility Functions

## Overview

This document provides detailed technical specifications for implementing the utility functions in Phase 3 of the codebase analyzer enhancement project. These functions build on the core analysis and visualization capabilities implemented in Phases 1 and 2, and provide additional tools to make the analyzer more user-friendly and powerful.

## 1. Function to Find All Paths Between Functions

### Purpose
To find all possible paths between two functions in the call graph, helping developers understand the flow of execution and dependencies between functions.

### Class Design

```python
class PathFinder:
    """Finds paths between nodes in a graph."""
    
    def __init__(self, call_graph: CallGraph):
        """Initialize path finder.
        
        Args:
            call_graph: CallGraph instance.
        """
        self.call_graph = call_graph
    
    def find_all_paths(self, source_function: str, target_function: str,
                      max_paths: int = None) -> List[List[str]]:
        """Find all paths between two functions.
        
        Args:
            source_function: ID of the source function.
            target_function: ID of the target function.
            max_paths: Maximum number of paths to find.
            
        Returns:
            List of paths, where each path is a list of function IDs.
        """
        # Implementation details
    
    def find_shortest_path(self, source_function: str, target_function: str) -> List[str]:
        """Find the shortest path between two functions.
        
        Args:
            source_function: ID of the source function.
            target_function: ID of the target function.
            
        Returns:
            List of function IDs representing the shortest path.
        """
        # Implementation details
    
    def find_critical_paths(self, source_function: str, target_function: str) -> List[List[str]]:
        """Find critical paths between two functions.
        
        Args:
            source_function: ID of the source function.
            target_function: ID of the target function.
            
        Returns:
            List of critical paths, where each path is a list of function IDs.
        """
        # Implementation details
```

### Implementation in CodebaseAnalyzer

```python
def find_all_paths(self, source_function: str, target_function: str,
                  max_paths: int = None) -> Dict[str, Any]:
    """Find all possible paths between two functions in the call graph.
    
    Args:
        source_function: ID of the source function.
        target_function: ID of the target function.
        max_paths: Maximum number of paths to find.
        
    Returns:
        Dictionary with path finding results.
    """
    # Implementation steps:
    # 1. Analyze call chains if not already analyzed
    # 2. Create a PathFinder instance
    # 3. Find all paths between the source and target functions
    # 4. Return path finding results
```

### CLI Integration

```python
# In CLI argument parser
parser.add_argument('--find-paths', action='store_true',
                    help='Find all possible paths between two functions')
parser.add_argument('--source-function', help='ID of the source function')
parser.add_argument('--target-function', help='ID of the target function')
parser.add_argument('--max-paths', type=int, default=None,
                    help='Maximum number of paths to find')
```

## 2. Function to Break Circular Dependencies

### Purpose
To identify and suggest fixes for circular dependencies in a codebase, helping developers improve the architecture and maintainability.

### Class Design

```python
class DependencyResolver:
    """Resolves dependency issues in a codebase."""
    
    def __init__(self, dependency_graph: DependencyGraph):
        """Initialize dependency resolver.
        
        Args:
            dependency_graph: DependencyGraph instance.
        """
        self.dependency_graph = dependency_graph
    
    def detect_circular_dependencies(self) -> List[List[str]]:
        """Detect circular dependencies in the graph.
        
        Returns:
            List of circular dependency chains, where each chain is a list of node IDs.
        """
        # Implementation details
    
    def suggest_resolution(self, circular_dependency: List[str],
                          strategy: str = 'extract') -> Dict[str, Any]:
        """Suggest a resolution for a circular dependency.
        
        Args:
            circular_dependency: List of node IDs forming a circular dependency.
            strategy: Resolution strategy ('extract', 'invert', 'interface').
            
        Returns:
            Dictionary with resolution suggestions.
        """
        # Implementation details
    
    def apply_resolution(self, circular_dependency: List[str],
                        strategy: str = 'extract') -> bool:
        """Apply a resolution to a circular dependency.
        
        Args:
            circular_dependency: List of node IDs forming a circular dependency.
            strategy: Resolution strategy ('extract', 'invert', 'interface').
            
        Returns:
            Whether the resolution was successful.
        """
        # Implementation details
```

### Implementation in CodebaseAnalyzer

```python
def break_circular_dependencies(self, resolution_strategy: str = 'extract') -> Dict[str, Any]:
    """Identify and suggest fixes for circular dependencies.
    
    Args:
        resolution_strategy: Resolution strategy ('extract', 'invert', 'interface').
        
    Returns:
        Dictionary with circular dependency resolution results.
    """
    # Implementation steps:
    # 1. Build dependency graph if not already built
    # 2. Create a DependencyResolver instance
    # 3. Detect circular dependencies
    # 4. Suggest resolutions for each circular dependency
    # 5. Return resolution results
```

### CLI Integration

```python
# In CLI argument parser
parser.add_argument('--break-circular-dependencies', action='store_true',
                    help='Identify and suggest fixes for circular dependencies')
parser.add_argument('--resolution-strategy', choices=['extract', 'invert', 'interface'],
                    default='extract', help='Strategy for resolving circular dependencies')
```

## 3. Function to Calculate Type Coverage Percentages

### Purpose
To calculate type coverage percentages across the codebase, helping developers track progress and identify areas for improvement.

### Enhancements to TypeAnalyzer Class

```python
class TypeAnalyzer:
    # Existing methods...
    
    def calculate_file_coverage(self, file_path: str) -> Dict[str, float]:
        """Calculate type coverage percentages for a file.
        
        Args:
            file_path: Path to the file.
            
        Returns:
            Dictionary mapping coverage categories to percentages.
        """
        # Implementation details
    
    def calculate_directory_coverage(self, directory_path: str) -> Dict[str, float]:
        """Calculate type coverage percentages for a directory.
        
        Args:
            directory_path: Path to the directory.
            
        Returns:
            Dictionary mapping coverage categories to percentages.
        """
        # Implementation details
    
    def calculate_project_coverage(self) -> Dict[str, float]:
        """Calculate type coverage percentages for the entire project.
        
        Returns:
            Dictionary mapping coverage categories to percentages.
        """
        # Implementation details
    
    def generate_coverage_report(self, coverage_level: str = 'project',
                               output_format: str = 'json') -> Dict[str, Any]:
        """Generate a type coverage report.
        
        Args:
            coverage_level: Level of coverage to report ('file', 'directory', 'project').
            output_format: Output format ('json', 'csv', 'text').
            
        Returns:
            Dictionary with coverage report data.
        """
        # Implementation details
```

### Implementation in CodebaseAnalyzer

```python
def calculate_type_coverage(self, coverage_level: str = 'project',
                           output_format: str = 'json',
                           output_path: str = None) -> Dict[str, Any]:
    """Calculate type coverage percentages across the codebase.
    
    Args:
        coverage_level: Level of coverage to calculate ('file', 'directory', 'project').
        output_format: Output format ('json', 'csv', 'text').
        output_path: Optional path to save the coverage report.
        
    Returns:
        Dictionary with type coverage results.
    """
    # Implementation steps:
    # 1. Analyze type coverage if not already analyzed
    # 2. Calculate coverage percentages at the specified level
    # 3. Generate a coverage report
    # 4. Export the report if output_path is provided
    # 5. Return coverage results
```

### CLI Integration

```python
# In CLI argument parser
parser.add_argument('--calculate-type-coverage', action='store_true',
                    help='Calculate type coverage percentages across the codebase')
parser.add_argument('--coverage-level', choices=['file', 'directory', 'project'],
                    default='project', help='Level of coverage to calculate')
parser.add_argument('--output-format', choices=['json', 'csv', 'text'],
                    default='json', help='Output format for the coverage report')
```

## 4. Function to Analyze Module Coupling

### Purpose
To analyze coupling between modules in a codebase, helping developers identify potential architectural issues and improve modularity.

### Class Design

```python
class CouplingAnalyzer:
    """Analyzes coupling between modules in a codebase."""
    
    def __init__(self, dependency_graph: DependencyGraph):
        """Initialize coupling analyzer.
        
        Args:
            dependency_graph: DependencyGraph instance.
        """
        self.dependency_graph = dependency_graph
    
    def calculate_afferent_coupling(self, module_id: str) -> int:
        """Calculate afferent coupling (incoming dependencies) for a module.
        
        Args:
            module_id: ID of the module.
            
        Returns:
            Afferent coupling value.
        """
        # Implementation details
    
    def calculate_efferent_coupling(self, module_id: str) -> int:
        """Calculate efferent coupling (outgoing dependencies) for a module.
        
        Args:
            module_id: ID of the module.
            
        Returns:
            Efferent coupling value.
        """
        # Implementation details
    
    def calculate_instability(self, module_id: str) -> float:
        """Calculate instability for a module.
        
        Args:
            module_id: ID of the module.
            
        Returns:
            Instability value (0-1).
        """
        # Implementation details
    
    def calculate_abstractness(self, module_id: str) -> float:
        """Calculate abstractness for a module.
        
        Args:
            module_id: ID of the module.
            
        Returns:
            Abstractness value (0-1).
        """
        # Implementation details
    
    def calculate_distance_from_main_sequence(self, module_id: str) -> float:
        """Calculate distance from the main sequence for a module.
        
        Args:
            module_id: ID of the module.
            
        Returns:
            Distance value (0-1).
        """
        # Implementation details
    
    def suggest_improvements(self, module_id: str,
                            coupling_threshold: float = 0.7) -> List[Dict[str, Any]]:
        """Suggest improvements for a module based on coupling analysis.
        
        Args:
            module_id: ID of the module.
            coupling_threshold: Threshold for flagging high coupling.
            
        Returns:
            List of improvement suggestions.
        """
        # Implementation details
```

### Implementation in CodebaseAnalyzer

```python
def analyze_module_coupling(self, coupling_threshold: float = 0.7,
                           suggest_improvements: bool = True) -> Dict[str, Any]:
    """Analyze coupling between modules.
    
    Args:
        coupling_threshold: Threshold for flagging high coupling.
        suggest_improvements: Whether to suggest improvements.
        
    Returns:
        Dictionary with coupling analysis results.
    """
    # Implementation steps:
    # 1. Build dependency graph if not already built
    # 2. Create a CouplingAnalyzer instance
    # 3. Calculate coupling metrics for each module
    # 4. Identify modules with high coupling
    # 5. Suggest improvements if requested
    # 6. Return analysis results
```

### CLI Integration

```python
# In CLI argument parser
parser.add_argument('--analyze-module-coupling', action='store_true',
                    help='Analyze coupling between modules')
parser.add_argument('--coupling-threshold', type=float, default=0.7,
                    help='Threshold for flagging high coupling')
parser.add_argument('--suggest-improvements', action='store_true',
                    help='Suggest improvements for modules with high coupling')
```

## 5. Function to Get Max Call Chain

### Purpose
To find the longest call chain in the codebase, helping developers identify potential performance issues or excessive complexity.

### Implementation in CodebaseAnalyzer

```python
def get_max_call_chain(self) -> Dict[str, Any]:
    """Find the longest call chain in the codebase.
    
    Returns:
        Dictionary with max call chain results.
    """
    # Implementation steps:
    # 1. Analyze call chains if not already analyzed
    # 2. Find the longest call chain
    # 3. Return the call chain and its length
```

### CLI Integration

```python
# In CLI argument parser
parser.add_argument('--get-max-call-chain', action='store_true',
                    help='Find the longest call chain in the codebase')
```

## 6. Function to Organize Imports

### Purpose
To organize imports in a file or across the codebase, helping developers maintain clean and consistent code.

### Implementation in CodebaseAnalyzer

```python
def organize_imports(self, file_path: str = None) -> Dict[str, Any]:
    """Organize imports in a file or across the codebase.
    
    Args:
        file_path: Optional path to the file to organize.
        
    Returns:
        Dictionary with import organization results.
    """
    # Implementation steps:
    # 1. Find relevant files (or use the specified file)
    # 2. Parse each file to extract imports
    # 3. Organize imports by type and name
    # 4. Update the files with organized imports
    # 5. Return organization results
```

### CLI Integration

```python
# In CLI argument parser
parser.add_argument('--organize-imports', action='store_true',
                    help='Organize imports in a file or across the codebase')
parser.add_argument('--file-path', help='Path to the file to organize')
```

## 7. Function to Extract Shared Code

### Purpose
To identify and extract shared code into common modules, helping developers improve code reuse and maintainability.

### Implementation in CodebaseAnalyzer

```python
def extract_shared_code(self, similarity_threshold: float = 0.8) -> Dict[str, Any]:
    """Extract shared code into common modules.
    
    Args:
        similarity_threshold: Threshold for considering code as similar.
        
    Returns:
        Dictionary with code extraction results.
    """
    # Implementation steps:
    # 1. Find all relevant files
    # 2. Parse each file to extract code blocks
    # 3. Identify similar code blocks across files
    # 4. Suggest common modules for shared code
    # 5. Return extraction results
```

### CLI Integration

```python
# In CLI argument parser
parser.add_argument('--extract-shared-code', action='store_true',
                    help='Extract shared code into common modules')
parser.add_argument('--similarity-threshold', type=float, default=0.8,
                    help='Threshold for considering code as similar')
```

## 8. Function to Determine Appropriate Shared Module

### Purpose
To determine the appropriate module for shared code, helping developers organize code logically and maintain a clean architecture.

### Implementation in CodebaseAnalyzer

```python
def determine_shared_module(self, code_block: str) -> Dict[str, Any]:
    """Determine the appropriate module for shared code.
    
    Args:
        code_block: Code block to analyze.
        
    Returns:
        Dictionary with module determination results.
    """
    # Implementation steps:
    # 1. Analyze the code block to determine its functionality
    # 2. Identify existing modules with similar functionality
    # 3. Suggest the most appropriate module for the code
    # 4. Return determination results
```

### CLI Integration

```python
# In CLI argument parser
parser.add_argument('--determine-shared-module', action='store_true',
                    help='Determine the appropriate module for shared code')
parser.add_argument('--code-block', help='Code block to analyze')
```

## Integration with Existing Code

The utility functions will be integrated into the existing `CodebaseAnalyzer` class, following the same patterns and conventions. The implementation will leverage the analysis and visualization functions implemented in Phases 1 and 2, and introduce new classes for specific utility tasks.

## Error Handling

All utility functions will include appropriate error handling to ensure robustness:

1. Input validation to check for invalid parameters
2. Exception handling for file I/O operations
3. Graceful degradation when operations fail
4. Informative error messages for debugging

## Testing Strategy

Each utility function will be tested with:

1. Unit tests for individual components
2. Integration tests for end-to-end functionality
3. Edge case tests for unusual inputs
4. Performance tests for large codebases

## Performance Considerations

To ensure good performance with large codebases:

1. Implement incremental processing where possible
2. Use caching for expensive operations
3. Add options to limit processing scope
4. Provide progress indicators for long-running operations

## Documentation

Each utility function will be documented with:

1. Comprehensive docstrings explaining purpose, parameters, and return values
2. Usage examples in the README
3. Detailed explanations in the user guide
4. CLI help text for command-line usage

