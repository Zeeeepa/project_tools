# Technical Specification: Phase 2 - Visualization Functions

## Overview

This document provides detailed technical specifications for implementing the visualization functions in Phase 2 of the codebase analyzer enhancement project. These functions build on the core analysis capabilities implemented in Phase 1 and provide visual representations of various aspects of the codebase.

## 1. Module Dependency Visualization

### Purpose
To visualize dependencies between modules in a codebase, helping developers understand the architecture and identify potential issues such as circular dependencies or excessive coupling.

### Class Design

```python
class VisualizationGenerator:
    """Generates visualizations for codebase analysis."""
    
    def __init__(self):
        """Initialize visualization generator."""
        self.graph_data = {}  # Dict[str, Any] - visualization data
    
    def generate_module_dependency_graph(self, dependency_graph: DependencyGraph,
                                        layout: str = 'force') -> Dict[str, Any]:
        """Generate a module dependency graph visualization.
        
        Args:
            dependency_graph: DependencyGraph instance.
            layout: Layout algorithm to use ('force', 'circular', 'hierarchical').
            
        Returns:
            Dictionary with visualization data.
        """
        # Implementation details
    
    def export_visualization(self, output_path: str, format: str = 'html') -> bool:
        """Export visualization to a file.
        
        Args:
            output_path: Path to save the visualization.
            format: Output format ('html', 'png', 'svg').
            
        Returns:
            Whether the export was successful.
        """
        # Implementation details
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the generator to a dictionary."""
        # Implementation details
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'VisualizationGenerator':
        """Create a generator from a dictionary."""
        # Implementation details
```

### Implementation in CodebaseAnalyzer

```python
def visualize_module_dependencies(self, layout: str = 'force',
                                 output_format: str = 'html',
                                 output_path: str = None) -> Dict[str, Any]:
    """Visualize dependencies between modules.
    
    Args:
        layout: Layout algorithm to use ('force', 'circular', 'hierarchical').
        output_format: Output format ('html', 'png', 'svg').
        output_path: Optional path to save the visualization.
        
    Returns:
        Dictionary with visualization data.
    """
    # Implementation steps:
    # 1. Build dependency graph if not already built
    # 2. Create a VisualizationGenerator instance
    # 3. Generate module dependency graph
    # 4. Export visualization if output_path is provided
    # 5. Return visualization data
```

### CLI Integration

```python
# In CLI argument parser
parser.add_argument('--visualize-module-dependencies', action='store_true',
                    help='Visualize dependencies between modules')
parser.add_argument('--output-format', choices=['html', 'png', 'svg'], default='html',
                    help='Output format for visualizations')
parser.add_argument('--layout', choices=['force', 'circular', 'hierarchical'], default='force',
                    help='Layout algorithm for visualizations')
```

## 2. Blast Radius Visualization

### Purpose
To visualize the impact of changes to a specific function or module, helping developers understand the potential consequences of modifications and plan testing accordingly.

### Enhancements to VisualizationGenerator Class

```python
class VisualizationGenerator:
    # Existing methods...
    
    def generate_blast_radius_graph(self, call_graph: CallGraph, target_function: str,
                                   impact_depth: int = 2) -> Dict[str, Any]:
        """Generate a blast radius visualization.
        
        Args:
            call_graph: CallGraph instance.
            target_function: ID of the target function.
            impact_depth: Depth of impact to visualize.
            
        Returns:
            Dictionary with visualization data.
        """
        # Implementation details
    
    def calculate_impact_severity(self, call_graph: CallGraph, target_function: str) -> Dict[str, float]:
        """Calculate impact severity for functions affected by changes to the target function.
        
        Args:
            call_graph: CallGraph instance.
            target_function: ID of the target function.
            
        Returns:
            Dictionary mapping function IDs to impact severity scores.
        """
        # Implementation details
```

### Implementation in CodebaseAnalyzer

```python
def visualize_blast_radius(self, target_function: str, impact_depth: int = 2,
                          output_format: str = 'html',
                          output_path: str = None) -> Dict[str, Any]:
    """Visualize the impact of changes to a specific function.
    
    Args:
        target_function: ID of the target function.
        impact_depth: Depth of impact to visualize.
        output_format: Output format ('html', 'png', 'svg').
        output_path: Optional path to save the visualization.
        
    Returns:
        Dictionary with visualization data.
    """
    # Implementation steps:
    # 1. Analyze call chains if not already analyzed
    # 2. Create a VisualizationGenerator instance
    # 3. Generate blast radius graph
    # 4. Export visualization if output_path is provided
    # 5. Return visualization data
```

### CLI Integration

```python
# In CLI argument parser
parser.add_argument('--visualize-blast-radius', metavar='TARGET_FUNCTION',
                    help='Visualize the impact of changes to a specific function')
parser.add_argument('--impact-depth', type=int, default=2,
                    help='Depth of impact to visualize')
```

## 3. Inheritance Graph Visualization

### Purpose
To visualize class inheritance hierarchies in a codebase, helping developers understand the object-oriented design and identify potential issues such as deep inheritance chains or multiple inheritance complexity.

### Enhancements to VisualizationGenerator Class

```python
class VisualizationGenerator:
    # Existing methods...
    
    def generate_inheritance_graph(self, base_class: str = None,
                                  max_depth: int = None) -> Dict[str, Any]:
        """Generate an inheritance graph visualization.
        
        Args:
            base_class: Optional ID of the base class to start from.
            max_depth: Maximum depth of inheritance to visualize.
            
        Returns:
            Dictionary with visualization data.
        """
        # Implementation details
```

### Implementation in CodebaseAnalyzer

```python
def visualize_inheritance_graph(self, base_class: str = None, max_depth: int = None,
                               output_format: str = 'html',
                               output_path: str = None) -> Dict[str, Any]:
    """Visualize class inheritance hierarchies.
    
    Args:
        base_class: Optional ID of the base class to start from.
        max_depth: Maximum depth of inheritance to visualize.
        output_format: Output format ('html', 'png', 'svg').
        output_path: Optional path to save the visualization.
        
    Returns:
        Dictionary with visualization data.
    """
    # Implementation steps:
    # 1. Analyze class inheritance if not already analyzed
    # 2. Create a VisualizationGenerator instance
    # 3. Generate inheritance graph
    # 4. Export visualization if output_path is provided
    # 5. Return visualization data
```

### CLI Integration

```python
# In CLI argument parser
parser.add_argument('--visualize-inheritance', action='store_true',
                    help='Visualize class inheritance hierarchies')
parser.add_argument('--base-class', help='Base class to start visualization from')
```

## 4. Usage Relationship Visualization

### Purpose
To visualize how symbols (functions, classes, variables) are used throughout the codebase, helping developers understand dependencies and identify potential refactoring opportunities.

### Enhancements to VisualizationGenerator Class

```python
class VisualizationGenerator:
    # Existing methods...
    
    def generate_usage_graph(self, target_symbol: str = None,
                            usage_type: str = None) -> Dict[str, Any]:
        """Generate a usage relationship visualization.
        
        Args:
            target_symbol: Optional ID of the target symbol.
            usage_type: Optional type of usage to visualize ('import', 'call', 'reference').
            
        Returns:
            Dictionary with visualization data.
        """
        # Implementation details
```

### Implementation in CodebaseAnalyzer

```python
def visualize_usage_relationships(self, target_symbol: str = None,
                                 usage_type: str = None,
                                 output_format: str = 'html',
                                 output_path: str = None) -> Dict[str, Any]:
    """Visualize how symbols are used throughout the codebase.
    
    Args:
        target_symbol: Optional ID of the target symbol.
        usage_type: Optional type of usage to visualize ('import', 'call', 'reference').
        output_format: Output format ('html', 'png', 'svg').
        output_path: Optional path to save the visualization.
        
    Returns:
        Dictionary with visualization data.
    """
    # Implementation steps:
    # 1. Analyze symbol usage if not already analyzed
    # 2. Create a VisualizationGenerator instance
    # 3. Generate usage graph
    # 4. Export visualization if output_path is provided
    # 5. Return visualization data
```

### CLI Integration

```python
# In CLI argument parser
parser.add_argument('--visualize-usage', action='store_true',
                    help='Visualize how symbols are used throughout the codebase')
parser.add_argument('--target-symbol', help='Target symbol to visualize usage for')
parser.add_argument('--usage-type', choices=['import', 'call', 'reference'],
                    help='Type of usage to visualize')
```

## 5. React Component Tree Visualization

### Purpose
To visualize the hierarchy and relationships between React components in a codebase, helping developers understand the component structure and identify potential issues such as prop drilling or excessive nesting.

### Class Design

```python
class ReactAnalyzer:
    """Analyzes React components in a codebase."""
    
    def __init__(self):
        """Initialize React analyzer."""
        self.components = {}  # Dict[str, Dict[str, Any]] - component_id -> metadata
        self.component_hierarchy = {}  # Dict[str, Set[str]] - parent_id -> set of child_ids
        self.props = {}  # Dict[str, Dict[str, str]] - component_id -> {prop_name: prop_type}
    
    def analyze_component(self, file_path: str, content: str):
        """Analyze React components in a file.
        
        Args:
            file_path: Path to the file.
            content: Content of the file.
        """
        # Implementation details
    
    def get_component_tree(self, root_component: str = None) -> Dict[str, Any]:
        """Get the component tree.
        
        Args:
            root_component: Optional ID of the root component.
            
        Returns:
            Dictionary with component tree data.
        """
        # Implementation details
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the analyzer to a dictionary."""
        # Implementation details
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ReactAnalyzer':
        """Create an analyzer from a dictionary."""
        # Implementation details
```

### Enhancements to VisualizationGenerator Class

```python
class VisualizationGenerator:
    # Existing methods...
    
    def generate_react_component_tree(self, react_analyzer: ReactAnalyzer,
                                     root_component: str = None,
                                     include_props: bool = False) -> Dict[str, Any]:
        """Generate a React component tree visualization.
        
        Args:
            react_analyzer: ReactAnalyzer instance.
            root_component: Optional ID of the root component.
            include_props: Whether to include props in the visualization.
            
        Returns:
            Dictionary with visualization data.
        """
        # Implementation details
```

### Implementation in CodebaseAnalyzer

```python
def visualize_react_components(self, root_component: str = None,
                              include_props: bool = False,
                              output_format: str = 'html',
                              output_path: str = None) -> Dict[str, Any]:
    """Visualize React component hierarchy and relationships.
    
    Args:
        root_component: Optional ID of the root component.
        include_props: Whether to include props in the visualization.
        output_format: Output format ('html', 'png', 'svg').
        output_path: Optional path to save the visualization.
        
    Returns:
        Dictionary with visualization data.
    """
    # Implementation steps:
    # 1. Find all relevant React files
    # 2. Create a ReactAnalyzer instance
    # 3. Analyze each file to extract component information
    # 4. Create a VisualizationGenerator instance
    # 5. Generate React component tree
    # 6. Export visualization if output_path is provided
    # 7. Return visualization data
```

### CLI Integration

```python
# In CLI argument parser
parser.add_argument('--visualize-react-components', action='store_true',
                    help='Visualize React component hierarchy and relationships')
parser.add_argument('--root-component', help='Root component to start visualization from')
parser.add_argument('--include-props', action='store_true',
                    help='Include props in the visualization')
```

## 6. HTTP Method Detection and Visualization

### Purpose
To detect and visualize HTTP endpoints and their relationships in a codebase, helping developers understand the API structure and identify potential issues such as inconsistent naming or missing endpoints.

### Class Design

```python
class APIAnalyzer:
    """Analyzes API endpoints in a codebase."""
    
    def __init__(self):
        """Initialize API analyzer."""
        self.endpoints = {}  # Dict[str, Dict[str, Any]] - endpoint_id -> metadata
        self.controllers = {}  # Dict[str, Set[str]] - controller_id -> set of endpoint_ids
    
    def analyze_endpoints(self, file_path: str, content: str, framework: str = None):
        """Analyze API endpoints in a file.
        
        Args:
            file_path: Path to the file.
            content: Content of the file.
            framework: Optional API framework ('express', 'flask', 'django', etc.).
        """
        # Implementation details
    
    def get_endpoints_by_method(self) -> Dict[str, List[str]]:
        """Get endpoints grouped by HTTP method.
        
        Returns:
            Dictionary mapping HTTP methods to lists of endpoint IDs.
        """
        # Implementation details
    
    def get_endpoints_by_controller(self) -> Dict[str, List[str]]:
        """Get endpoints grouped by controller.
        
        Returns:
            Dictionary mapping controller IDs to lists of endpoint IDs.
        """
        # Implementation details
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the analyzer to a dictionary."""
        # Implementation details
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'APIAnalyzer':
        """Create an analyzer from a dictionary."""
        # Implementation details
```

### Enhancements to VisualizationGenerator Class

```python
class VisualizationGenerator:
    # Existing methods...
    
    def generate_http_method_graph(self, api_analyzer: APIAnalyzer,
                                  group_by: str = 'method') -> Dict[str, Any]:
        """Generate an HTTP method visualization.
        
        Args:
            api_analyzer: APIAnalyzer instance.
            group_by: How to group endpoints ('method', 'path', 'controller').
            
        Returns:
            Dictionary with visualization data.
        """
        # Implementation details
```

### Implementation in CodebaseAnalyzer

```python
def visualize_http_methods(self, api_framework: str = None,
                          group_by: str = 'method',
                          output_format: str = 'html',
                          output_path: str = None) -> Dict[str, Any]:
    """Visualize HTTP endpoints and their relationships.
    
    Args:
        api_framework: Optional API framework ('express', 'flask', 'django', etc.).
        group_by: How to group endpoints ('method', 'path', 'controller').
        output_format: Output format ('html', 'png', 'svg').
        output_path: Optional path to save the visualization.
        
    Returns:
        Dictionary with visualization data.
    """
    # Implementation steps:
    # 1. Find all relevant API files
    # 2. Create an APIAnalyzer instance
    # 3. Analyze each file to extract endpoint information
    # 4. Create a VisualizationGenerator instance
    # 5. Generate HTTP method graph
    # 6. Export visualization if output_path is provided
    # 7. Return visualization data
```

### CLI Integration

```python
# In CLI argument parser
parser.add_argument('--visualize-http-methods', action='store_true',
                    help='Visualize HTTP endpoints and their relationships')
parser.add_argument('--api-framework', choices=['express', 'flask', 'django'],
                    help='API framework used in the codebase')
parser.add_argument('--group-by', choices=['method', 'path', 'controller'], default='method',
                    help='How to group endpoints in the visualization')
```

## Integration with Existing Code

The visualization functions will be integrated into the existing `CodebaseAnalyzer` class, following the same patterns and conventions. The implementation will leverage the analysis functions implemented in Phase 1, and introduce new classes for specific visualization tasks.

## Visualization Libraries

The implementation will use the following libraries for visualization:

1. **NetworkX**: For creating and manipulating graph structures
2. **Plotly**: For generating interactive visualizations
3. **Matplotlib**: For generating static visualizations
4. **Rich**: For console-based visualizations

## Error Handling

All visualization functions will include appropriate error handling to ensure robustness:

1. Input validation to check for invalid parameters
2. Exception handling for visualization generation
3. Graceful degradation when visualization fails
4. Informative error messages for debugging

## Testing Strategy

Each visualization function will be tested with:

1. Unit tests for individual components
2. Integration tests for end-to-end functionality
3. Visual tests to verify the correctness of visualizations
4. Performance tests for large codebases

## Performance Considerations

To ensure good performance with large codebases:

1. Implement lazy loading for visualization data
2. Use sampling for very large graphs
3. Add options to limit visualization scope
4. Provide progress indicators for long-running operations

## Documentation

Each visualization function will be documented with:

1. Comprehensive docstrings explaining purpose, parameters, and return values
2. Usage examples in the README
3. Sample visualizations in the user guide
4. CLI help text for command-line usage

