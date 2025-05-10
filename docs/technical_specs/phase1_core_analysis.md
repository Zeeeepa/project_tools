# Technical Specification: Phase 1 - Core Analysis Functions

## Overview

This document provides detailed technical specifications for implementing the core analysis functions in Phase 1 of the codebase analyzer enhancement project. These functions form the foundation for the visualization and utility functions that will be implemented in later phases.

## 1. Call Chain Analysis

### Purpose
To analyze and visualize the call chains between functions in a codebase, helping developers understand the flow of execution and dependencies between functions.

### Class Design

```python
class CallGraph:
    """Represents a call graph of functions in a codebase."""
    
    def __init__(self):
        """Initialize call graph."""
        self.nodes = {}  # Dict[str, Set[str]] - function_id -> set of called function_ids
        self.metadata = {}  # Dict[str, Dict[str, Any]] - function_id -> metadata
    
    def add_node(self, function_id: str, metadata: Dict[str, Any] = None):
        """Add a function node to the graph."""
        # Implementation details
    
    def add_edge(self, caller: str, callee: str, metadata: Dict[str, Any] = None):
        """Add a call edge to the graph."""
        # Implementation details
    
    def get_callees(self, function_id: str) -> Set[str]:
        """Get functions called by the given function."""
        # Implementation details
    
    def get_callers(self, function_id: str) -> Set[str]:
        """Get functions that call the given function."""
        # Implementation details
    
    def get_call_chain(self, function_id: str, max_depth: int = None) -> Dict[str, Any]:
        """Get the call chain starting from the given function."""
        # Implementation details
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the graph to a dictionary."""
        # Implementation details
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CallGraph':
        """Create a graph from a dictionary."""
        # Implementation details
    
    def visualize(self) -> Tree:
        """Visualize the graph as a tree."""
        # Implementation details
```

### Implementation in CodebaseAnalyzer

```python
def analyze_call_chains(self, max_depth: int = None, include_patterns: List[str] = None, 
                        exclude_patterns: List[str] = None) -> Dict[str, Any]:
    """Analyze call chains in the codebase.
    
    Args:
        max_depth: Maximum depth of call chains to analyze.
        include_patterns: List of glob patterns to include.
        exclude_patterns: List of glob patterns to exclude.
        
    Returns:
        Dictionary with call chain analysis results.
    """
    # Implementation steps:
    # 1. Find all relevant files
    # 2. Parse each file to extract function definitions and calls
    # 3. Build the call graph
    # 4. Analyze call chains
    # 5. Return analysis results
```

### CLI Integration

```python
# In CLI argument parser
parser.add_argument('--analyze-call-chains', action='store_true', 
                    help='Analyze call chains between functions')
parser.add_argument('--max-chain-depth', type=int, default=None,
                    help='Maximum depth of call chains to analyze')
```

## 2. Dependency Graph Traversal

### Purpose
To traverse and analyze dependency graphs, helping developers understand the relationships between modules and components in a codebase.

### Enhancements to DependencyGraph Class

```python
class DependencyGraph:
    # Existing methods...
    
    def traverse_bfs(self, start_node: str, max_depth: int = None) -> Dict[str, Any]:
        """Traverse the graph using breadth-first search.
        
        Args:
            start_node: ID of the starting node.
            max_depth: Maximum depth to traverse.
            
        Returns:
            Dictionary with traversal results.
        """
        # Implementation details
    
    def traverse_dfs(self, start_node: str, max_depth: int = None) -> Dict[str, Any]:
        """Traverse the graph using depth-first search.
        
        Args:
            start_node: ID of the starting node.
            max_depth: Maximum depth to traverse.
            
        Returns:
            Dictionary with traversal results.
        """
        # Implementation details
    
    def find_paths(self, start_node: str, end_node: str, max_paths: int = None) -> List[List[str]]:
        """Find paths between two nodes.
        
        Args:
            start_node: ID of the starting node.
            end_node: ID of the ending node.
            max_paths: Maximum number of paths to find.
            
        Returns:
            List of paths, where each path is a list of node IDs.
        """
        # Implementation details
    
    def get_subgraph(self, nodes: Set[str]) -> 'DependencyGraph':
        """Get a subgraph containing only the specified nodes.
        
        Args:
            nodes: Set of node IDs to include in the subgraph.
            
        Returns:
            DependencyGraph instance representing the subgraph.
        """
        # Implementation details
```

### Implementation in CodebaseAnalyzer

```python
def traverse_dependency_graph(self, start_node: str, traversal_type: str = 'bfs',
                             max_depth: int = None) -> Dict[str, Any]:
    """Traverse the dependency graph.
    
    Args:
        start_node: ID of the starting node.
        traversal_type: Type of traversal ('bfs' or 'dfs').
        max_depth: Maximum depth to traverse.
        
    Returns:
        Dictionary with traversal results.
    """
    # Implementation steps:
    # 1. Validate input parameters
    # 2. Choose traversal method based on traversal_type
    # 3. Perform traversal
    # 4. Return traversal results
```

### CLI Integration

```python
# In CLI argument parser
parser.add_argument('--traverse-dependencies', metavar='START_NODE',
                    help='Traverse dependency graph starting from the specified node')
parser.add_argument('--traversal-type', choices=['bfs', 'dfs'], default='bfs',
                    help='Type of traversal (breadth-first or depth-first)')
parser.add_argument('--max-depth', type=int, default=None,
                    help='Maximum depth to traverse')
```

## 3. Dead Code Detection with Filtering

### Purpose
To detect unused code in a codebase with configurable filters, helping developers identify and remove dead code to improve maintainability.

### Class Design

```python
class CodeUsageAnalyzer:
    """Analyzes code usage in a codebase."""
    
    def __init__(self):
        """Initialize code usage analyzer."""
        self.defined_symbols = {}  # Dict[str, Set[str]] - file_path -> set of defined symbols
        self.used_symbols = {}  # Dict[str, Set[str]] - file_path -> set of used symbols
        self.symbol_metadata = {}  # Dict[str, Dict[str, Any]] - symbol_id -> metadata
    
    def add_defined_symbol(self, file_path: str, symbol: str, metadata: Dict[str, Any] = None):
        """Add a defined symbol."""
        # Implementation details
    
    def add_used_symbol(self, file_path: str, symbol: str):
        """Add a used symbol."""
        # Implementation details
    
    def get_unused_symbols(self, exclude_patterns: List[str] = None) -> Dict[str, List[str]]:
        """Get unused symbols.
        
        Args:
            exclude_patterns: List of regex patterns to exclude from analysis.
            
        Returns:
            Dictionary mapping file paths to lists of unused symbols.
        """
        # Implementation details
    
    def get_unused_files(self) -> List[str]:
        """Get files that are never imported or used.
        
        Returns:
            List of file paths that are never imported or used.
        """
        # Implementation details
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the analyzer to a dictionary."""
        # Implementation details
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CodeUsageAnalyzer':
        """Create an analyzer from a dictionary."""
        # Implementation details
```

### Implementation in CodebaseAnalyzer

```python
def detect_dead_code(self, include_patterns: List[str] = None, 
                    exclude_patterns: List[str] = None) -> Dict[str, Any]:
    """Detect dead code in the codebase.
    
    Args:
        include_patterns: List of glob patterns to include.
        exclude_patterns: List of glob patterns to exclude.
        
    Returns:
        Dictionary with dead code detection results.
    """
    # Implementation steps:
    # 1. Find all relevant files
    # 2. Create a CodeUsageAnalyzer instance
    # 3. Analyze each file to extract defined and used symbols
    # 4. Identify unused symbols and files
    # 5. Return detection results
```

### CLI Integration

```python
# In CLI argument parser
parser.add_argument('--detect-dead-code', action='store_true',
                    help='Detect dead code in the codebase')
parser.add_argument('--exclude-patterns', nargs='+',
                    help='Regex patterns to exclude from dead code detection')
parser.add_argument('--include-patterns', nargs='+',
                    help='Glob patterns to include in dead code detection')
```

## 4. Type Resolution

### Purpose
To resolve and analyze type annotations in a codebase, helping developers understand the type system and improve type coverage.

### Class Design

```python
class TypeAnalyzer:
    """Analyzes type annotations in a codebase."""
    
    def __init__(self):
        """Initialize type analyzer."""
        self.type_annotations = {}  # Dict[str, Dict[str, str]] - file_path -> {symbol: type}
        self.type_metadata = {}  # Dict[str, Dict[str, Any]] - symbol_id -> metadata
    
    def add_type_annotation(self, file_path: str, symbol: str, type_annotation: str, 
                           metadata: Dict[str, Any] = None):
        """Add a type annotation."""
        # Implementation details
    
    def resolve_type(self, type_annotation: str) -> Dict[str, Any]:
        """Resolve a type annotation.
        
        Args:
            type_annotation: Type annotation string.
            
        Returns:
            Dictionary with resolved type information.
        """
        # Implementation details
    
    def get_type_coverage(self, file_path: str = None) -> Dict[str, Any]:
        """Get type coverage statistics.
        
        Args:
            file_path: Optional file path to get coverage for.
            
        Returns:
            Dictionary with type coverage statistics.
        """
        # Implementation details
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the analyzer to a dictionary."""
        # Implementation details
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TypeAnalyzer':
        """Create an analyzer from a dictionary."""
        # Implementation details
```

### Implementation in CodebaseAnalyzer

```python
def resolve_types(self, type_format: str = 'simple') -> Dict[str, Any]:
    """Resolve and analyze type annotations in the codebase.
    
    Args:
        type_format: Format of type information ('simple' or 'detailed').
        
    Returns:
        Dictionary with type resolution results.
    """
    # Implementation steps:
    # 1. Find all relevant files
    # 2. Create a TypeAnalyzer instance
    # 3. Analyze each file to extract type annotations
    # 4. Resolve types and calculate coverage
    # 5. Return resolution results
```

### CLI Integration

```python
# In CLI argument parser
parser.add_argument('--resolve-types', action='store_true',
                    help='Resolve and analyze type annotations')
parser.add_argument('--type-format', choices=['simple', 'detailed'], default='simple',
                    help='Format of type information')
```

## 5. Comprehensive Type Coverage Analysis

### Purpose
To provide detailed analysis of type coverage in a codebase, helping developers identify areas for improvement and track progress.

### Enhancements to TypeAnalyzer Class

```python
class TypeAnalyzer:
    # Existing methods...
    
    def analyze_parameter_types(self, file_path: str = None) -> Dict[str, Any]:
        """Analyze function parameter type annotations.
        
        Args:
            file_path: Optional file path to analyze.
            
        Returns:
            Dictionary with parameter type analysis results.
        """
        # Implementation details
    
    def analyze_return_types(self, file_path: str = None) -> Dict[str, Any]:
        """Analyze function return type annotations.
        
        Args:
            file_path: Optional file path to analyze.
            
        Returns:
            Dictionary with return type analysis results.
        """
        # Implementation details
    
    def analyze_variable_types(self, file_path: str = None) -> Dict[str, Any]:
        """Analyze variable type annotations.
        
        Args:
            file_path: Optional file path to analyze.
            
        Returns:
            Dictionary with variable type analysis results.
        """
        # Implementation details
    
    def calculate_coverage_percentages(self) -> Dict[str, float]:
        """Calculate type coverage percentages.
        
        Returns:
            Dictionary mapping coverage categories to percentages.
        """
        # Implementation details
```

### Implementation in CodebaseAnalyzer

```python
def analyze_type_coverage(self, coverage_threshold: float = None) -> Dict[str, Any]:
    """Analyze type coverage in the codebase.
    
    Args:
        coverage_threshold: Optional threshold for flagging low coverage.
        
    Returns:
        Dictionary with type coverage analysis results.
    """
    # Implementation steps:
    # 1. Find all relevant files
    # 2. Create a TypeAnalyzer instance
    # 3. Analyze each file to extract type annotations
    # 4. Calculate coverage percentages
    # 5. Identify areas for improvement
    # 6. Return analysis results
```

### CLI Integration

```python
# In CLI argument parser
parser.add_argument('--analyze-type-coverage', action='store_true',
                    help='Analyze type coverage in the codebase')
parser.add_argument('--coverage-threshold', type=float, default=None,
                    help='Threshold for flagging low type coverage')
```

## Integration with Existing Code

The new functions will be integrated into the existing `CodebaseAnalyzer` class, following the same patterns and conventions. The implementation will leverage the existing `DependencyGraph` and `CodeMetrics` classes where appropriate, and introduce new classes for specific analysis tasks.

## Error Handling

All functions will include appropriate error handling to ensure robustness:

1. Input validation to check for invalid parameters
2. Exception handling for file I/O operations
3. Graceful degradation when analysis fails for specific files
4. Informative error messages for debugging

## Testing Strategy

Each function will be tested with:

1. Unit tests for individual components
2. Integration tests for end-to-end functionality
3. Edge case tests for unusual inputs
4. Performance tests for large codebases

## Performance Considerations

To ensure good performance with large codebases:

1. Implement incremental analysis where possible
2. Use caching for expensive operations
3. Add options to limit analysis scope
4. Provide progress indicators for long-running operations

## Documentation

Each function will be documented with:

1. Comprehensive docstrings explaining purpose, parameters, and return values
2. Usage examples in the README
3. Detailed explanations in the user guide
4. CLI help text for command-line usage

