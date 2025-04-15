"""
Project Context Manager for LLM integration.

This module provides functionality to manage project context for LLM-assisted code generation.
"""

import os
import json
import time
from typing import Dict, List, Optional, Any
from pathlib import Path
from rich.console import Console

console = Console()

class ProjectContext:
    """Manages project context for LLM-assisted code generation."""
    
    def __init__(self, project_path: str):
        """Initialize project context.
        
        Args:
            project_path: Path to the project directory.
        """
        self.project_path = Path(project_path)
        self.context_file = self.project_path / ".project_genie_context.json"
        self.context = self._load_context()
        
    def _load_context(self) -> Dict[str, Any]:
        """Load project context from file.
        
        Returns:
            Project context dictionary.
        """
        if not self.context_file.exists():
            return self._create_default_context()
        
        try:
            with open(self.context_file, "r") as f:
                return json.load(f)
        except Exception as e:
            console.print(f"[yellow]Warning: Failed to load context file: {str(e)}. Creating new context.[/yellow]")
            return self._create_default_context()
    
    def _create_default_context(self) -> Dict[str, Any]:
        """Create default project context.
        
        Returns:
            Default project context dictionary.
        """
        return {
            "project_name": self.project_path.name,
            "created_at": time.time(),
            "updated_at": time.time(),
            "components": [],
            "requirements": [],
            "history": []
        }
    
    def save(self) -> None:
        """Save project context to file."""
        self.context["updated_at"] = time.time()
        
        try:
            with open(self.context_file, "w") as f:
                json.dump(self.context, f, indent=2)
        except Exception as e:
            console.print(f"[red]Error saving context file: {str(e)}[/red]")
    
    def add_component(self, component_type: str, name: str, path: str, description: str = "") -> None:
        """Add a component to the project context.
        
        Args:
            component_type: Type of component (e.g., "frontend", "backend", "model").
            name: Name of the component.
            path: Path to the component relative to project root.
            description: Description of the component.
        """
        component = {
            "type": component_type,
            "name": name,
            "path": path,
            "description": description,
            "created_at": time.time()
        }
        
        self.context["components"].append(component)
        self.save()
    
    def add_requirement(self, requirement: str, category: str = "feature") -> None:
        """Add a requirement to the project context.
        
        Args:
            requirement: Requirement description.
            category: Category of the requirement (e.g., "feature", "fix", "enhancement").
        """
        req = {
            "description": requirement,
            "category": category,
            "created_at": time.time(),
            "status": "pending"
        }
        
        self.context["requirements"].append(req)
        self.save()
    
    def add_history_entry(self, action: str, description: str, metadata: Optional[Dict[str, Any]] = None) -> None:
        """Add an entry to the project history.
        
        Args:
            action: Action performed (e.g., "generate", "validate", "refine").
            description: Description of the action.
            metadata: Additional metadata about the action.
        """
        entry = {
            "action": action,
            "description": description,
            "timestamp": time.time(),
            "metadata": metadata or {}
        }
        
        self.context["history"].append(entry)
        self.save()
    
    def get_components(self, component_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get components from the project context.
        
        Args:
            component_type: Optional type to filter by.
            
        Returns:
            List of components.
        """
        if component_type is None:
            return self.context["components"]
        
        return [c for c in self.context["components"] if c["type"] == component_type]
    
    def get_requirements(self, status: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get requirements from the project context.
        
        Args:
            status: Optional status to filter by.
            
        Returns:
            List of requirements.
        """
        if status is None:
            return self.context["requirements"]
        
        return [r for r in self.context["requirements"] if r["status"] == status]
    
    def get_history(self, action: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get history entries from the project context.
        
        Args:
            action: Optional action to filter by.
            
        Returns:
            List of history entries.
        """
        if action is None:
            return self.context["history"]
        
        return [h for h in self.context["history"] if h["action"] == action]
    
    def update_requirement_status(self, index: int, status: str) -> None:
        """Update the status of a requirement.
        
        Args:
            index: Index of the requirement in the requirements list.
            status: New status (e.g., "pending", "completed", "failed").
        """
        if 0 <= index < len(self.context["requirements"]):
            self.context["requirements"][index]["status"] = status
            self.context["requirements"][index]["updated_at"] = time.time()
            self.save()
        else:
            console.print(f"[red]Error: Requirement index {index} out of range[/red]")
    
    def get_project_summary(self) -> Dict[str, Any]:
        """Get a summary of the project.
        
        Returns:
            Project summary dictionary.
        """
        return {
            "project_name": self.context["project_name"],
            "created_at": self.context["created_at"],
            "updated_at": self.context["updated_at"],
            "component_count": len(self.context["components"]),
            "requirement_count": len(self.context["requirements"]),
            "history_count": len(self.context["history"])
        }
