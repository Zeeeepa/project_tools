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
