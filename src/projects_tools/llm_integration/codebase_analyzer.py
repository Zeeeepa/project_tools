"""
Codebase Analyzer module for LLM integration.

This module provides functionality to analyze a codebase and extract insights.
"""

import os
import re
import ast
import json
import subprocess
from typing import Dict, List, Optional, Any, Tuple, Set
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.tree import Tree
import networkx as nx
import plotly.graph_objects as go
from plotly.subplots import make_subplots

console = Console()

class DependencyGraph:
    """Represents a dependency graph of a codebase."""
    
    def __init__(self):
        """Initialize dependency graph."""
        self.nodes = {}  # type: Dict[str, Set[str]]
        self.metadata = {}  # type: Dict[str, Dict[str, Any]]
    
    def add_node(self, node_id: str, metadata: Dict[str, Any] = None):
        """Add a node to the graph.
        
        Args:
            node_id: ID of the node.
            metadata: Optional metadata for the node.
        """
        if node_id not in self.nodes:
            self.nodes[node_id] = set()
            self.metadata[node_id] = metadata or {}
    
    def add_edge(self, from_node: str, to_node: str, metadata: Dict[str, Any] = None):
        """Add an edge to the graph.
        
        Args:
            from_node: ID of the source node.
            to_node: ID of the target node.
            metadata: Optional metadata for the edge.
        """
        self.add_node(from_node)
        self.add_node(to_node)
        self.nodes[from_node].add(to_node)
        
        # Store edge metadata
        edge_key = f"{from_node}_{to_node}"
        self.metadata[edge_key] = metadata or {}
    
    def get_dependencies(self, node_id: str) -> Set[str]:
        """Get dependencies of a node.
        
        Args:
            node_id: ID of the node.
            
        Returns:
            Set of node IDs that the given node depends on.
        """
        return self.nodes.get(node_id, set())
    
    def get_dependents(self, node_id: str) -> Set[str]:
        """Get dependents of a node.
        
        Args:
            node_id: ID of the node.
            
        Returns:
            Set of node IDs that depend on the given node.
        """
        dependents = set()
        for node, deps in self.nodes.items():
            if node_id in deps:
                dependents.add(node)
        return dependents
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the graph to a dictionary.
        
        Returns:
            Dictionary representation of the graph.
        """
        return {
            "nodes": {node: list(deps) for node, deps in self.nodes.items()},
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DependencyGraph':
        """Create a graph from a dictionary.
        
        Args:
            data: Dictionary representation of the graph.
            
        Returns:
            DependencyGraph instance.
        """
        graph = cls()
        graph.nodes = {node: set(deps) for node, deps in data.get("nodes", {}).items()}
        graph.metadata = data.get("metadata", {})
        return graph
    
    def visualize(self) -> Tree:
        """Visualize the graph as a tree.
        
        Returns:
            Rich Tree object.
        """
        tree = Tree("Dependency Graph")
        
        for node, deps in self.nodes.items():
            node_tree = tree.add(f"[bold]{node}[/bold]")
            
            if deps:
                for dep in sorted(deps):
                    node_tree.add(f"→ {dep}")
            else:
                node_tree.add("[italic]No dependencies[/italic]")
        
        return tree


class CodeMetrics:
    """Metrics for code quality and complexity."""
    
    def __init__(self):
        """Initialize code metrics."""
        self.metrics = {}  # type: Dict[str, Dict[str, Any]]
    
    def add_file_metrics(self, file_path: str, metrics: Dict[str, Any]):
        """Add metrics for a file.
        
        Args:
            file_path: Path to the file.
            metrics: Dictionary of metrics.
        """
        self.metrics[file_path] = metrics
    
    def get_file_metrics(self, file_path: str) -> Dict[str, Any]:
        """Get metrics for a file.
        
        Args:
            file_path: Path to the file.
            
        Returns:
            Dictionary of metrics.
        """
        return self.metrics.get(file_path, {})
    
    def get_average_complexity(self) -> float:
        """Get average cyclomatic complexity across all files.
        
        Returns:
            Average complexity.
        """
        complexities = []
        for file_metrics in self.metrics.values():
            if "cyclomatic_complexity" in file_metrics:
                complexities.append(file_metrics["cyclomatic_complexity"])
        
        if not complexities:
            return 0.0
        
        return sum(complexities) / len(complexities)
    
    def get_highest_complexity_files(self, limit: int = 5) -> List[Tuple[str, float]]:
        """Get files with highest cyclomatic complexity.
        
        Args:
            limit: Maximum number of files to return.
            
        Returns:
            List of (file_path, complexity) tuples.
        """
        files_with_complexity = []
        for file_path, metrics in self.metrics.items():
            if "cyclomatic_complexity" in metrics:
                files_with_complexity.append((file_path, metrics["cyclomatic_complexity"]))
        
        return sorted(files_with_complexity, key=lambda x: x[1], reverse=True)[:limit]
    
    def to_dict(self) -> Dict[str, Dict[str, Any]]:
        """Convert metrics to a dictionary.
        
        Returns:
            Dictionary representation of metrics.
        """
        return self.metrics
    
    @classmethod
    def from_dict(cls, data: Dict[str, Dict[str, Any]]) -> 'CodeMetrics':
        """Create metrics from a dictionary.
        
        Args:
            data: Dictionary representation of metrics.
            
        Returns:
            CodeMetrics instance.
        """
        metrics = cls()
        metrics.metrics = data
        return metrics


class CodebaseAnalyzer:
    """Analyzes a codebase and extracts insights."""
    
    def __init__(self, project_path: str):
        """Initialize codebase analyzer.
        
        Args:
            project_path: Path to the project directory.
        """
        self.project_path = Path(project_path)
        self.dependency_graph = DependencyGraph()
        self.code_metrics = CodeMetrics()
    
    def analyze_codebase(self, include_patterns: List[str] = None, exclude_patterns: List[str] = None) -> Dict[str, Any]:
        """Analyze the codebase.
        
        Args:
            include_patterns: List of glob patterns to include.
            exclude_patterns: List of glob patterns to exclude.
            
        Returns:
            Dictionary of analysis results.
        """
        console.print(Panel(f"[bold blue]Analyzing codebase at {self.project_path}[/bold blue]"))
        
        # Find all relevant files
        files = self._find_files(include_patterns, exclude_patterns)
        
        # Analyze each file
        for file_path in files:
            self._analyze_file(file_path)
        
        # Build dependency graph
        self._build_dependency_graph(files)
        
        # Calculate metrics
        self._calculate_metrics(files)
        
        # Return analysis results
        return {
            "dependency_graph": self.dependency_graph.to_dict(),
            "code_metrics": self.code_metrics.to_dict(),
            "summary": self._generate_summary()
        }
    
    def _find_files(self, include_patterns: List[str] = None, exclude_patterns: List[str] = None) -> List[str]:
        """Find files in the project.
        
        Args:
            include_patterns: List of glob patterns to include.
            exclude_patterns: List of glob patterns to exclude.
            
        Returns:
            List of file paths.
        """
        include_patterns = include_patterns or ["**/*.py", "**/*.js", "**/*.jsx", "**/*.ts", "**/*.tsx"]
        exclude_patterns = exclude_patterns or ["**/node_modules/**", "**/__pycache__/**", "**/venv/**", "**/build/**", "**/dist/**"]
        
        files = []
        for pattern in include_patterns:
            for file_path in self.project_path.glob(pattern):
                if file_path.is_file():
                    # Check if file should be excluded
                    exclude = False
                    for exclude_pattern in exclude_patterns:
                        if file_path.match(exclude_pattern):
                            exclude = True
                            break
                    
                    if not exclude:
                        files.append(str(file_path.relative_to(self.project_path)))
        
        return files
    
    def _analyze_file(self, file_path: str):
        """Analyze a file.
        
        Args:
            file_path: Path to the file to analyze.
        """
        full_path = os.path.join(self.project_path, file_path)
        
        try:
            with open(full_path, 'r') as f:
                content = f.read()
            
            # Determine file type
            file_ext = os.path.splitext(file_path)[1].lower()
            
            if file_ext == '.py':
                self._analyze_python_file(file_path, content)
            elif file_ext in ['.js', '.jsx', '.ts', '.tsx']:
                self._analyze_javascript_file(file_path, content)
        except Exception as e:
            console.print(f"[red]Error analyzing file {file_path}: {str(e)}[/red]")
    
    def _analyze_python_file(self, file_path: str, content: str):
        """Analyze a Python file.
        
        Args:
            file_path: Path to the file to analyze.
            content: Content of the file.
        """
        try:
            tree = ast.parse(content)
            
            # Extract imports
            imports = []
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for name in node.names:
                        imports.append(name.name)
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        for name in node.names:
                            imports.append(f"{node.module}.{name.name}")
            
            # Store imports in dependency graph
            for imp in imports:
                self.dependency_graph.add_edge(file_path, imp, {"type": "import"})
            
            # Calculate cyclomatic complexity
            complexity = self._calculate_python_complexity(tree)
            
            # Store metrics
            self.code_metrics.add_file_metrics(file_path, {
                "lines_of_code": len(content.splitlines()),
                "imports": imports,
                "cyclomatic_complexity": complexity
            })
        except SyntaxError:
            console.print(f"[yellow]Syntax error in {file_path}, skipping analysis[/yellow]")
    
    def _analyze_javascript_file(self, file_path: str, content: str):
        """Analyze a JavaScript/TypeScript file.
        
        Args:
            file_path: Path to the file to analyze.
            content: Content of the file.
        """
        # Extract imports using regex (simplified)
        import_regex = r'import\s+(?:{[^}]*}|[^{}\n;]+)\s+from\s+[\'"]([^\'"]+)[\'"]'
        require_regex = r'(?:const|let|var)\s+(?:{[^}]*}|[^{}\n;]+)\s+=\s+require\([\'"]([^\'"]+)[\'"]\)'
        
        imports = []
        for match in re.finditer(import_regex, content):
            imports.append(match.group(1))
        
        for match in re.finditer(require_regex, content):
            imports.append(match.group(1))
        
        # Store imports in dependency graph
        for imp in imports:
            self.dependency_graph.add_edge(file_path, imp, {"type": "import"})
        
        # Calculate cyclomatic complexity (simplified)
        complexity = content.count('if ') + content.count('else ') + content.count('for ') + \
                    content.count('while ') + content.count('switch ') + content.count('case ') + \
                    content.count('&&') + content.count('||') + content.count('?') + 1
        
        # Store metrics
        self.code_metrics.add_file_metrics(file_path, {
            "lines_of_code": len(content.splitlines()),
            "imports": imports,
            "cyclomatic_complexity": complexity
        })
    
    def _calculate_python_complexity(self, tree: ast.AST) -> int:
        """Calculate cyclomatic complexity of Python code.
        
        Args:
            tree: AST of the Python code.
            
        Returns:
            Cyclomatic complexity.
        """
        complexity = 1  # Base complexity
        
        for node in ast.walk(tree):
            if isinstance(node, (ast.If, ast.While, ast.For)):
                complexity += 1
            elif isinstance(node, ast.BoolOp) and isinstance(node.op, (ast.And, ast.Or)):
                complexity += len(node.values) - 1
            elif isinstance(node, ast.Try):
                complexity += len(node.handlers)
        
        return complexity
    
    def _build_dependency_graph(self, files: List[str]):
        """Build dependency graph for the codebase.
        
        Args:
            files: List of file paths.
        """
        # Add all files as nodes
        for file_path in files:
            self.dependency_graph.add_node(file_path, {"type": "file"})
    
    def _calculate_metrics(self, files: List[str]):
        """Calculate metrics for the codebase.
        
        Args:
            files: List of file paths.
        """
        # Calculate lines of code
        total_loc = sum(self.code_metrics.get_file_metrics(file).get("lines_of_code", 0) for file in files)
        
        # Store project-level metrics
        self.code_metrics.add_file_metrics("__project__", {
            "total_files": len(files),
            "total_lines_of_code": total_loc,
            "average_complexity": self.code_metrics.get_average_complexity()
        })
    
    def _generate_summary(self) -> Dict[str, Any]:
        """Generate a summary of the analysis.
        
        Returns:
            Dictionary with summary information.
        """
        project_metrics = self.code_metrics.get_file_metrics("__project__")
        highest_complexity = self.code_metrics.get_highest_complexity_files(5)
        
        return {
            "total_files": project_metrics.get("total_files", 0),
            "total_lines_of_code": project_metrics.get("total_lines_of_code", 0),
            "average_complexity": project_metrics.get("average_complexity", 0),
            "highest_complexity_files": highest_complexity,
            "architectural_patterns": self._detect_architectural_patterns(),
            "improvement_suggestions": self._generate_improvement_suggestions()
        }
    
    def _detect_architectural_patterns(self) -> List[str]:
        """Detect architectural patterns in the codebase.
        
        Returns:
            List of detected patterns.
        """
        patterns = []
        
        # Check for MVC pattern
        has_models = any("model" in file.lower() for file in self.dependency_graph.nodes)
        has_views = any("view" in file.lower() for file in self.dependency_graph.nodes)
        has_controllers = any("controller" in file.lower() for file in self.dependency_graph.nodes)
        
        if has_models and has_views and has_controllers:
            patterns.append("Model-View-Controller (MVC)")
        
        # Check for Repository pattern
        has_repositories = any("repository" in file.lower() or "repo" in file.lower() for file in self.dependency_graph.nodes)
        
        if has_repositories:
            patterns.append("Repository Pattern")
        
        # Check for Service pattern
        has_services = any("service" in file.lower() for file in self.dependency_graph.nodes)
        
        if has_services:
            patterns.append("Service Pattern")
        
        return patterns
    
    def _generate_improvement_suggestions(self) -> List[Dict[str, Any]]:
        """Generate improvement suggestions for the codebase.
        
        Returns:
            List of improvement suggestions.
        """
        suggestions = []
        
        # Check for high complexity files
        high_complexity_files = self.code_metrics.get_highest_complexity_files(3)
        
        if high_complexity_files:
            for file_path, complexity in high_complexity_files:
                if complexity > 10:
                    suggestions.append({
                        "type": "complexity",
                        "file": file_path,
                        "description": f"High cyclomatic complexity ({complexity}). Consider refactoring to reduce complexity.",
                        "priority": "high" if complexity > 20 else "medium"
                    })
        
        # Check for circular dependencies
        for node in self.dependency_graph.nodes:
            deps = self.dependency_graph.get_dependencies(node)
            for dep in deps:
                if dep in self.dependency_graph.nodes and node in self.dependency_graph.get_dependencies(dep):
                    suggestions.append({
                        "type": "circular_dependency",
                        "files": [node, dep],
                        "description": f"Circular dependency between {node} and {dep}. Consider refactoring to break the cycle.",
                        "priority": "high"
                    })
        
        return suggestions
    
    def visualize_dependency_graph(self) -> Tree:
        """Visualize the dependency graph.
        
        Returns:
            Rich Tree object.
        """
        return self.dependency_graph.visualize()
    
    def visualize_react_component_tree(self, root_component: str = None) -> Dict[str, Any]:
        """Visualize React component hierarchy and relationships.
        
        Args:
            root_component: Optional root component to start visualization from.
                If not provided, will attempt to find the main component.
                
        Returns:
            Dictionary with visualization data.
        """
        # Find React components in the codebase
        react_files = [file for file in self.dependency_graph.nodes 
                      if file.endswith(('.jsx', '.tsx', '.js', '.ts'))]
        
        if not react_files:
            console.print("[yellow]No React component files found in the codebase.[/yellow]")
            return {"error": "No React component files found"}
        
        # Create a graph for React components
        G = nx.DiGraph()
        
        # Map of component names to file paths
        component_files = {}
        
        # Extract component relationships
        for file_path in react_files:
            try:
                full_path = os.path.join(self.project_path, file_path)
                with open(full_path, 'r') as f:
                    content = f.read()
                
                # Extract component name from file (simplified approach)
                component_name = os.path.basename(file_path).split('.')[0]
                component_files[component_name] = file_path
                G.add_node(component_name, file=file_path)
                
                # Find imported components
                import_regex = r'import\s+(\w+)\s+from\s+[\'"]([^\'"]+)[\'"]'
                for match in re.finditer(import_regex, content):
                    imported_name = match.group(1)
                    imported_path = match.group(2)
                    
                    # Check if this is likely a component (starts with uppercase)
                    if imported_name[0].isupper():
                        G.add_node(imported_name)
                        G.add_edge(component_name, imported_name)
                
                # Find component usage within JSX/TSX
                component_usage_regex = r'<(\w+)[\s/>]'
                for match in re.finditer(component_usage_regex, content):
                    used_component = match.group(1)
                    
                    # Only consider components (starts with uppercase) and not HTML tags
                    if used_component[0].isupper() and used_component != component_name:
                        if used_component not in G:
                            G.add_node(used_component)
                        G.add_edge(component_name, used_component)
            
            except Exception as e:
                console.print(f"[yellow]Error analyzing React component {file_path}: {str(e)}[/yellow]")
        
        # If root component is not specified, try to find it
        if root_component is None:
            # Look for components with "App" or "Main" in the name
            potential_roots = [node for node in G.nodes if "App" in node or "Main" in node]
            if potential_roots:
                root_component = potential_roots[0]
            else:
                # Use the component with the most outgoing edges
                root_component = sorted(G.nodes, key=lambda n: G.out_degree(n), reverse=True)[0]
        
        # Create a tree starting from the root component
        tree = nx.bfs_tree(G, root_component)
        
        # Create a plotly figure
        fig = go.Figure()
        
        # Create a network graph
        pos = nx.spring_layout(tree)
        
        # Add edges
        edge_x = []
        edge_y = []
        for edge in tree.edges():
            x0, y0 = pos[edge[0]]
            x1, y1 = pos[edge[1]]
            edge_x.extend([x0, x1, None])
            edge_y.extend([y0, y1, None])
            
        fig.add_trace(go.Scatter(
            x=edge_x, y=edge_y,
            line=dict(width=0.5, color='#888'),
            hoverinfo='none',
            mode='lines'))
        
        # Add nodes
        node_x = []
        node_y = []
        node_text = []
        for node in tree.nodes():
            x, y = pos[node]
            node_x.append(x)
            node_y.append(y)
            file_info = f" ({component_files.get(node, 'external')})" if node in component_files else ""
            node_text.append(f"{node}{file_info}")
            
        fig.add_trace(go.Scatter(
            x=node_x, y=node_y,
            mode='markers+text',
            marker=dict(
                showscale=True,
                colorscale='YlGnBu',
                size=10,
                colorbar=dict(
                    thickness=15,
                    title='Node Connections',
                    xanchor='left',
                    titleside='right'
                ),
                line_width=2),
            text=node_text,
            textposition="top center",
            hoverinfo='text'))
        
        fig.update_layout(
            title=f'React Component Tree (Root: {root_component})',
            showlegend=False,
            hovermode='closest',
            margin=dict(b=20, l=5, r=5, t=40),
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False))
        
        # Return visualization data
        return {
            "visualization_type": "react_component_tree",
            "root_component": root_component,
            "component_count": len(tree.nodes),
            "plotly_figure": fig,
            "component_files": component_files
        }
    
    def visualize_inheritance_graph(self, language: str = "python") -> Dict[str, Any]:
        """Visualize class inheritance hierarchies.
        
        Args:
            language: Programming language to analyze. Currently supports "python".
                
        Returns:
            Dictionary with visualization data.
        """
        if language.lower() != "python":
            console.print(f"[yellow]Inheritance visualization for {language} is not yet supported. Using Python.[/yellow]")
            language = "python"
        
        # Find Python files in the codebase
        python_files = [file for file in self.dependency_graph.nodes if file.endswith('.py')]
        
        if not python_files:
            console.print("[yellow]No Python files found in the codebase.[/yellow]")
            return {"error": "No Python files found"}
        
        # Create a graph for class inheritance
        G = nx.DiGraph()
        
        # Map of class names to file paths
        class_files = {}
        
        # Extract class inheritance relationships
        for file_path in python_files:
            try:
                full_path = os.path.join(self.project_path, file_path)
                with open(full_path, 'r') as f:
                    content = f.read()
                
                try:
                    tree = ast.parse(content)
                    
                    for node in ast.walk(tree):
                        if isinstance(node, ast.ClassDef):
                            class_name = node.name
                            class_files[class_name] = file_path
                            G.add_node(class_name, file=file_path)
                            
                            # Add inheritance relationships
                            for base in node.bases:
                                if isinstance(base, ast.Name):
                                    base_name = base.id
                                    G.add_node(base_name)
                                    # Child inherits from parent, so edge direction is from parent to child
                                    G.add_edge(base_name, class_name)
                                elif isinstance(base, ast.Attribute):
                                    # Handle cases like module.BaseClass
                                    base_name = base.attr
                                    G.add_node(base_name)
                                    G.add_edge(base_name, class_name)
                
                except SyntaxError:
                    console.print(f"[yellow]Syntax error in {file_path}, skipping inheritance analysis[/yellow]")
            
            except Exception as e:
                console.print(f"[yellow]Error analyzing inheritance in {file_path}: {str(e)}[/yellow]")
        
        # Create a plotly figure
        fig = go.Figure()
        
        # Use hierarchical layout if possible
        try:
            pos = nx.nx_agraph.graphviz_layout(G, prog='dot')
        except:
            pos = nx.spring_layout(G)
        
        # Add edges
        edge_x = []
        edge_y = []
        for edge in G.edges():
            x0, y0 = pos[edge[0]]
            x1, y1 = pos[edge[1]]
            edge_x.extend([x0, x1, None])
            edge_y.extend([y0, y1, None])
            
        fig.add_trace(go.Scatter(
            x=edge_x, y=edge_y,
            line=dict(width=0.5, color='#888'),
            hoverinfo='none',
            mode='lines'))
        
        # Add nodes
        node_x = []
        node_y = []
        node_text = []
        node_colors = []
        
        # Identify root classes (no parents)
        root_classes = [node for node in G.nodes() if G.in_degree(node) == 0 and G.out_degree(node) > 0]
        
        for node in G.nodes():
            x, y = pos[node]
            node_x.append(x)
            node_y.append(y)
            
            # Add file info if available
            file_info = f" ({class_files.get(node, 'external')})" if node in class_files else ""
            node_text.append(f"{node}{file_info}")
            
            # Color root classes differently
            if node in root_classes:
                node_colors.append(1)
            else:
                node_colors.append(0.5)
            
        fig.add_trace(go.Scatter(
            x=node_x, y=node_y,
            mode='markers+text',
            marker=dict(
                color=node_colors,
                showscale=True,
                colorscale='Viridis',
                size=15,
                colorbar=dict(
                    thickness=15,
                    title='Class Type',
                    xanchor='left',
                    titleside='right'
                ),
                line_width=2),
            text=node_text,
            textposition="top center",
            hoverinfo='text'))
        
        fig.update_layout(
            title='Class Inheritance Hierarchy',
            showlegend=False,
            hovermode='closest',
            margin=dict(b=20, l=5, r=5, t=40),
            annotations=[
                dict(
                    text="Root classes are darker",
                    showarrow=False,
                    xref="paper", yref="paper",
                    x=0.01, y=0.01
                )
            ],
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False))
        
        # Return visualization data
        return {
            "visualization_type": "inheritance_graph",
            "class_count": len(G.nodes),
            "root_classes": root_classes,
            "plotly_figure": fig,
            "class_files": class_files
        }
    
    def export_analysis(self, output_path: str) -> bool:
        """Export analysis results to a file.
        
        Args:
            output_path: Path to save the analysis results.
            
        Returns:
            Whether the export was successful.
        """
        try:
            analysis = {
                "dependency_graph": self.dependency_graph.to_dict(),
                "code_metrics": self.code_metrics.to_dict(),
                "summary": self._generate_summary()
            }
            
            with open(output_path, 'w') as f:
                json.dump(analysis, f, indent=2)
            
            console.print(f"[green]Analysis exported to {output_path}[/green]")
            return True
        except Exception as e:
            console.print(f"[red]Error exporting analysis: {str(e)}[/red]")
            return False
    
    def import_analysis(self, input_path: str) -> bool:
        """Import analysis results from a file.
        
        Args:
            input_path: Path to the analysis file.
            
        Returns:
            Whether the import was successful.
        """
        try:
            with open(input_path, 'r') as f:
                analysis = json.load(f)
            
            self.dependency_graph = DependencyGraph.from_dict(analysis.get("dependency_graph", {}))
            self.code_metrics = CodeMetrics.from_dict(analysis.get("code_metrics", {}))
            
            console.print(f"[green]Analysis imported from {input_path}[/green]")
            return True
        except Exception as e:
            console.print(f"[red]Error importing analysis: {str(e)}[/red]")
            return False
    
    def visualize_module_dependency(self) -> Dict[str, Any]:
        """Visualize dependencies between modules.
        
        Returns:
            Dictionary with visualization data.
        """
        # Create a graph for module dependencies
        G = nx.DiGraph()
        
        # Extract module names from file paths
        module_map = {}
        for file_path in self.dependency_graph.nodes:
            if not isinstance(file_path, str) or not os.path.isfile(os.path.join(self.project_path, file_path)):
                continue
                
            # Extract module name (directory or package)
            parts = file_path.split(os.sep)
            if len(parts) > 1:
                module_name = parts[0]
                if module_name not in module_map:
                    module_map[module_name] = []
                module_map[module_name].append(file_path)
        
        # Add modules as nodes
        for module, files in module_map.items():
            G.add_node(module, files=files, file_count=len(files))
        
        # Add dependencies between modules
        for source_module, source_files in module_map.items():
            for source_file in source_files:
                dependencies = self.dependency_graph.get_dependencies(source_file)
                for dep in dependencies:
                    if isinstance(dep, str) and os.path.isfile(os.path.join(self.project_path, dep)):
                        dep_parts = dep.split(os.sep)
                        if len(dep_parts) > 1:
                            target_module = dep_parts[0]
                            if target_module in module_map and target_module != source_module:
                                if not G.has_edge(source_module, target_module):
                                    G.add_edge(source_module, target_module, weight=1)
                                else:
                                    G[source_module][target_module]['weight'] += 1
        
        # Create a plotly figure
        fig = go.Figure()
        
        # Use a layout that works well for module dependencies
        pos = nx.spring_layout(G, k=0.5, iterations=50)
        
        # Add edges with varying thickness based on weight
        edge_x = []
        edge_y = []
        edge_weights = []
        
        for source, target, data in G.edges(data=True):
            x0, y0 = pos[source]
            x1, y1 = pos[target]
            edge_x.extend([x0, x1, None])
            edge_y.extend([y0, y1, None])
            weight = data.get('weight', 1)
            edge_weights.append(weight)
        
        # Add edges
        fig.add_trace(go.Scatter(
            x=edge_x, y=edge_y,
            line=dict(width=1, color='#888'),
            hoverinfo='none',
            mode='lines'))
        
        # Add nodes with size based on file count
        node_x = []
        node_y = []
        node_text = []
        node_sizes = []
        
        # Identify root classes (no parents)
        root_classes = [node for node in G.nodes() if G.in_degree(node) == 0 and G.out_degree(node) > 0]
        
        for node in G.nodes():
            x, y = pos[node]
            node_x.append(x)
            node_y.append(y)
            
            # Add file info if available
            file_info = f" ({G.nodes[node].get('files', 'external')})" if node in G.nodes[node].get('files', []) else ""
            node_text.append(f"{node}{file_info}")
            
            # Color root classes differently
            if node in root_classes:
                node_sizes.append(100)
            else:
                node_sizes.append(50)
            
        fig.add_trace(go.Scatter(
            x=node_x, y=node_y,
            mode='markers+text',
            marker=dict(
                color=node_sizes,
                showscale=True,
                colorscale='YlOrRd',
                size=node_sizes,
                colorbar=dict(
                    thickness=15,
                    title='File Count',
                    xanchor='left',
                    titleside='right'
                ),
                line_width=2),
            text=list(G.nodes()),
            textposition="top center",
            hovertext=node_text,
            hoverinfo='text'))
        
        fig.update_layout(
            title='Module Dependency Graph',
            showlegend=False,
            hovermode='closest',
            margin=dict(b=20, l=5, r=5, t=40),
            annotations=[
                dict(
                    text="Root classes are larger",
                    showarrow=False,
                    xref="paper", yref="paper",
                    x=0.01, y=0.01
                )
            ],
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False))
        
        # Return visualization data
        return {
            "visualization_type": "module_dependency",
            "module_count": len(G.nodes),
            "dependency_count": len(G.edges),
            "plotly_figure": fig,
            "modules": {module: G.nodes[module].get('file_count', 0) for module in G.nodes()}
        }
    
    def visualize_blast_radius(self, target_file: str) -> Dict[str, Any]:
        """Visualize the impact of changes to a specific file.
        
        Args:
            target_file: Path to the file to analyze.
            
        Returns:
            Dictionary with visualization data.
        """
        if target_file not in self.dependency_graph.nodes:
            console.print(f"[yellow]File {target_file} not found in the analyzed codebase.[/yellow]")
            return {"error": f"File {target_file} not found"}
        
        # Create a graph for blast radius visualization
        G = nx.DiGraph()
        
        # Add the target file
        G.add_node(target_file, level=0, type="target")
        
        # Find direct dependents (files that import the target)
        direct_dependents = self.dependency_graph.get_dependents(target_file)
        for dep in direct_dependents:
            G.add_node(dep, level=1, type="direct")
            G.add_edge(target_file, dep)
        
        # Find indirect dependents (files that import the direct dependents)
        for direct_dep in direct_dependents:
            indirect_dependents = self.dependency_graph.get_dependents(direct_dep)
            for indirect_dep in indirect_dependents:
                if indirect_dep not in G:
                    G.add_node(indirect_dep, level=2, type="indirect")
                G.add_edge(direct_dep, indirect_dep)
        
        # Create a plotly figure
        fig = go.Figure()
        
        # Use a layout that shows the blast radius clearly
        pos = nx.spring_layout(G, k=0.5, iterations=50)
        
        # Add edges
        edge_x = []
        edge_y = []
        for edge in G.edges():
            x0, y0 = pos[edge[0]]
            x1, y1 = pos[edge[1]]
            edge_x.extend([x0, x1, None])
            edge_y.extend([y0, y1, None])
            
        fig.add_trace(go.Scatter(
            x=edge_x, y=edge_y,
            line=dict(width=0.5, color='#888'),
            hoverinfo='none',
            mode='lines'))
        
        # Add nodes with different colors based on level
        for level, color in [(0, 'red'), (1, 'orange'), (2, 'yellow')]:
            level_nodes = [node for node, data in G.nodes(data=True) if data.get('level') == level]
            if not level_nodes:
                continue
                
            node_x = []
            node_y = []
            node_text = []
            
            for node in level_nodes:
                x, y = pos[node]
                node_x.append(x)
                node_y.append(y)
                node_text.append(node)
                
            fig.add_trace(go.Scatter(
                x=node_x, y=node_y,
                mode='markers+text',
                marker=dict(
                    size=15,
                    color=color,
                    line_width=2),
                text=node_text,
                textposition="top center",
                name=["Target", "Direct Impact", "Indirect Impact"][level],
                hoverinfo='text'))
        
        fig.update_layout(
            title=f'Blast Radius for {os.path.basename(target_file)}',
            showlegend=True,
            hovermode='closest',
            margin=dict(b=20, l=5, r=5, t=40),
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False))
        
        # Calculate impact metrics
        direct_impact = len(direct_dependents)
        indirect_impact = len([n for n, d in G.nodes(data=True) if d.get('level') == 2])
        total_impact = direct_impact + indirect_impact
        
        # Return visualization data
        return {
            "visualization_type": "blast_radius",
            "target_file": target_file,
            "direct_impact": direct_impact,
            "indirect_impact": indirect_impact,
            "total_impact": total_impact,
            "impact_percentage": round(total_impact / len(self.dependency_graph.nodes) * 100, 2) if self.dependency_graph.nodes else 0,
            "plotly_figure": fig
        }
    
    def visualize_http_endpoints(self) -> Dict[str, Any]:
        """Detect and visualize HTTP endpoints and their relationships.
        
        Returns:
            Dictionary with visualization data.
        """
        # Find files that might contain HTTP endpoints
        potential_files = []
        for file_path in self.dependency_graph.nodes:
            if isinstance(file_path, str) and os.path.isfile(os.path.join(self.project_path, file_path)):
                # Look for files that might contain HTTP endpoints
                if any(keyword in file_path.lower() for keyword in ['route', 'api', 'endpoint', 'controller', 'view', 'handler']):
                    potential_files.append(file_path)
        
        if not potential_files:
            console.print("[yellow]No potential HTTP endpoint files found in the codebase.[/yellow]")
            return {"error": "No potential HTTP endpoint files found"}
        
        # Create a graph for HTTP endpoints
        G = nx.DiGraph()
        
        # Patterns to detect HTTP endpoints
        patterns = {
            'flask': {
                'pattern': r'@(?:app|blueprint)\.(?:route|get|post|put|delete|patch)\s*\(\s*[\'"]([^\'"]+)[\'"]',
                'method_pattern': r'@(?:app|blueprint)\.(\w+)\s*\(\s*[\'"][^\'"]+[\'"]'
            },
            'django': {
                'pattern': r'path\s*\(\s*[\'"]([^\'"]+)[\'"]',
                'method_pattern': r'@(?:api_view|require_http_methods)\s*\(\s*\[([^\]]+)\]'
            },
            'express': {
                'pattern': r'(?:app|router)\.(?:get|post|put|delete|patch)\s*\(\s*[\'"]([^\'"]+)[\'"]',
                'method_pattern': r'(?:app|router)\.(\w+)\s*\(\s*[\'"][^\'"]+[\'"]'
            },
            'fastapi': {
                'pattern': r'@(?:app|router)\.(?:get|post|put|delete|patch)\s*\(\s*[\'"]([^\'"]+)[\'"]',
                'method_pattern': r'@(?:app|router)\.(\w+)\s*\(\s*[\'"][^\'"]+[\'"]'
            }
        }
        
        # Extract HTTP endpoints
        endpoints = []
        
        for file_path in potential_files:
            try:
                full_path = os.path.join(self.project_path, file_path)
                with open(full_path, 'r') as f:
                    content = f.read()
                
                for framework, regex in patterns.items():
                    # Find routes/paths
                    route_matches = re.finditer(regex['pattern'], content)
                    for route_match in route_matches:
                        route = route_match.group(1)
                        
                        # Find HTTP method
                        method = 'GET'  # Default
                        method_matches = re.finditer(regex['method_pattern'], content)
                        for method_match in method_matches:
                            if framework in ['flask', 'express', 'fastapi']:
                                method = method_match.group(1).upper()
                            elif framework == 'django':
                                methods_str = method_match.group(1)
                                if 'POST' in methods_str:
                                    method = 'POST'
                                elif 'PUT' in methods_str:
                                    method = 'PUT'
                                elif 'DELETE' in methods_str:
                                    method = 'DELETE'
                                elif 'PATCH' in methods_str:
                                    method = 'PATCH'
                        
                        endpoint_id = f"{method}:{route}"
                        endpoints.append({
                            'id': endpoint_id,
                            'method': method,
                            'route': route,
                            'file': file_path,
                            'framework': framework
                        })
                        
                        G.add_node(endpoint_id, method=method, route=route, file=file_path, framework=framework)
            
            except Exception as e:
                console.print(f"[yellow]Error analyzing HTTP endpoints in {file_path}: {str(e)}[/yellow]")
        
        # Add relationships between endpoints (based on route hierarchy)
        for i, endpoint1 in enumerate(endpoints):
            for j, endpoint2 in enumerate(endpoints):
                if i != j:
                    # Check if endpoint2's route is a sub-route of endpoint1
                    if endpoint2['route'].startswith(endpoint1['route'] + '/'):
                        G.add_edge(endpoint1['id'], endpoint2['id'], type='hierarchy')
        
        # Create a plotly figure
        fig = go.Figure()
        
        # Use a layout that works well for API endpoints
        pos = nx.spring_layout(G, k=0.5, iterations=50)
        
        # Add edges
        edge_x = []
        edge_y = []
        for edge in G.edges():
            x0, y0 = pos[edge[0]]
            x1, y1 = pos[edge[1]]
            edge_x.extend([x0, x1, None])
            edge_y.extend([y0, y1, None])
            
        fig.add_trace(go.Scatter(
            x=edge_x, y=edge_y,
            line=dict(width=0.5, color='#888'),
            hoverinfo='none',
            mode='lines'))
        
        # Define colors for HTTP methods
        method_colors = {
            'GET': 'blue',
            'POST': 'green',
            'PUT': 'orange',
            'DELETE': 'red',
            'PATCH': 'purple',
            'OPTIONS': 'gray',
            'HEAD': 'brown'
        }
        
        # Group nodes by HTTP method
        for method, color in method_colors.items():
            method_nodes = [node for node, data in G.nodes(data=True) if data.get('method') == method]
            if not method_nodes:
                continue
                
            node_x = []
            node_y = []
            node_text = []
            
            for node in method_nodes:
                x, y = pos[node]
                node_x.append(x)
                node_y.append(y)
                
                # Create hover text with endpoint details
                data = G.nodes[node]
                node_text.append(f"{data.get('method', 'Unknown')} {data.get('route', 'Unknown')}<br>File: {data.get('file', 'Unknown')}<br>Framework: {data.get('framework', 'Unknown')}")
                
            fig.add_trace(go.Scatter(
                x=node_x, y=node_y,
                mode='markers+text',
                marker=dict(
                    size=15,
                    color=color,
                    line_width=2),
                text=[G.nodes[node].get('route', '') for node in method_nodes],
                textposition="top center",
                name=method,
                hovertext=node_text,
                hoverinfo='text'))
        
        fig.update_layout(
            title='HTTP Endpoints',
            showlegend=True,
            hovermode='closest',
            margin=dict(b=20, l=5, r=5, t=40),
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False))
        
        # Return visualization data
        return {
            "visualization_type": "http_endpoints",
            "endpoint_count": len(endpoints),
            "methods": {method: len([e for e in endpoints if e['method'] == method]) for method in set(e['method'] for e in endpoints)},
            "frameworks": {framework: len([e for e in endpoints if e['framework'] == framework]) for framework in set(e['framework'] for e in endpoints)},
            "plotly_figure": fig,
            "endpoints": endpoints
        }
    
    def visualize_usage_relationships(self, symbol_name: str = None) -> Dict[str, Any]:
        """Visualize how symbols are used throughout the codebase.
        
        Args:
            symbol_name: Optional name of the symbol to visualize.
                If not provided, will visualize the most used symbols.
                
        Returns:
            Dictionary with visualization data.
        """
        # Find all Python files in the codebase
        python_files = [file for file in self.dependency_graph.nodes if isinstance(file, str) and file.endswith('.py')]
        
        if not python_files:
            console.print("[yellow]No Python files found in the codebase.[/yellow]")
            return {"error": "No Python files found"}
        
        # Extract symbol definitions and usages
        symbol_definitions = {}  # file -> [symbols defined]
        symbol_usages = {}  # file -> {symbol -> count}
        
        for file_path in python_files:
            try:
                full_path = os.path.join(self.project_path, file_path)
                with open(full_path, 'r') as f:
                    content = f.read()
                
                try:
                    tree = ast.parse(content)
                    
                    # Find symbol definitions
                    definitions = []
                    for node in ast.walk(tree):
                        if isinstance(node, ast.ClassDef):
                            definitions.append(node.name)
                        elif isinstance(node, ast.FunctionDef):
                            definitions.append(node.name)
                        elif isinstance(node, ast.Name) and isinstance(node.ctx, ast.Store):
                            definitions.append(node.id)
                    
                    symbol_definitions[file_path] = definitions
                    
                    # Find symbol usages
                    usages = {}
                    for node in ast.walk(tree):
                        if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load):
                            symbol = node.id
                            if symbol not in usages:
                                usages[symbol] = 0
                            usages[symbol] += 1
                    
                    symbol_usages[file_path] = usages
                
                except SyntaxError:
                    console.print(f"[yellow]Syntax error in {file_path}, skipping symbol analysis[/yellow]")
            
            except Exception as e:
                console.print(f"[yellow]Error analyzing symbols in {file_path}: {str(e)}[/yellow]")
        
        # Create a graph for symbol usage
        G = nx.DiGraph()
        
        # If a specific symbol is provided, focus on that symbol
        if symbol_name:
            # Find files that define the symbol
            defining_files = [file for file, symbols in symbol_definitions.items() if symbol_name in symbols]
            
            if not defining_files:
                console.print(f"[yellow]Symbol '{symbol_name}' not found in any file definitions.[/yellow]")
                return {"error": f"Symbol '{symbol_name}' not found"}
            
            # Add the symbol as a central node
            G.add_node(symbol_name, type='symbol')
            
            # Add defining files
            for file in defining_files:
                G.add_node(file, type='defining_file')
                G.add_edge(file, symbol_name, type='defines')
            
            # Add files that use the symbol
            for file, usages in symbol_usages.items():
                if symbol_name in usages:
                    if file not in G:
                        G.add_node(file, type='using_file')
                    G.add_edge(symbol_name, file, type='used_by', count=usages[symbol_name])
        else:
            # Find the most used symbols
            all_usages = {}
            for file, usages in symbol_usages.items():
                for symbol, count in usages.items():
                    if symbol not in all_usages:
                        all_usages[symbol] = 0
                    all_usages[symbol] += count
            
            # Get top 10 most used symbols
            top_symbols = sorted(all_usages.items(), key=lambda x: x[1], reverse=True)[:10]
            
            for symbol, count in top_symbols:
                # Add the symbol as a node
                G.add_node(symbol, type='symbol', usage_count=count)
                
                # Find files that define the symbol
                defining_files = [file for file, symbols in symbol_definitions.items() if symbol in symbols]
                
                # Add defining files
                for file in defining_files:
                    if file not in G:
                        G.add_node(file, type='file')
                    G.add_edge(file, symbol, type='defines')
                
                # Add files that use the symbol
                for file, usages in symbol_usages.items():
                    if symbol in usages:
                        if file not in G:
                            G.add_node(file, type='file')
                        G.add_edge(symbol, file, type='used_by', count=usages[symbol])
        
        # Create a plotly figure
        fig = go.Figure()
        
        # Use a layout that works well for symbol usage
        pos = nx.spring_layout(G, k=0.5, iterations=50)
        
        # Add edges
        edge_x = []
        edge_y = []
        for edge in G.edges():
            x0, y0 = pos[edge[0]]
            x1, y1 = pos[edge[1]]
            edge_x.extend([x0, x1, None])
            edge_y.extend([y0, y1, None])
            
        fig.add_trace(go.Scatter(
            x=edge_x, y=edge_y,
            line=dict(width=0.5, color='#888'),
            hoverinfo='none',
            mode='lines'))
        
        # Add symbol nodes
        symbol_nodes = [node for node, data in G.nodes(data=True) if data.get('type') == 'symbol']
        if symbol_nodes:
            node_x = []
            node_y = []
            node_text = []
            node_sizes = []
            
            for node in symbol_nodes:
                x, y = pos[node]
                node_x.append(x)
                node_y.append(y)
                node_text.append(node)
                
                # Size based on usage count
                usage_count = G.nodes[node].get('usage_count', 10)
                node_sizes.append(10 + usage_count / 2)
                
            fig.add_trace(go.Scatter(
                x=node_x, y=node_y,
                mode='markers+text',
                marker=dict(
                    size=node_sizes,
                    color='red',
                    line_width=2),
                text=node_text,
                textposition="top center",
                name='Symbols',
                hoverinfo='text'))
        
        # Add file nodes
        file_nodes = [node for node, data in G.nodes(data=True) if data.get('type') != 'symbol']
        if file_nodes:
            node_x = []
            node_y = []
            node_text = []
            
            for node in file_nodes:
                x, y = pos[node]
                node_x.append(x)
                node_y.append(y)
                node_text.append(node)
                
            fig.add_trace(go.Scatter(
                x=node_x, y=node_y,
                mode='markers+text',
                marker=dict(
                    size=8,
                    color='blue',
                    line_width=2),
                text=node_text,
                textposition="top center",
                name='Files',
                hoverinfo='text'))
        
        title = f'Symbol Usage: {symbol_name}' if symbol_name else 'Top Symbol Usages'
        fig.update_layout(
            title=title,
            showlegend=True,
            hovermode='closest',
            margin=dict(b=20, l=5, r=5, t=40),
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False))
        
        # Return visualization data
        return {
            "visualization_type": "usage_relationships",
            "symbol": symbol_name,
            "symbol_count": len(symbol_nodes),
            "file_count": len(file_nodes),
            "plotly_figure": fig
        }
