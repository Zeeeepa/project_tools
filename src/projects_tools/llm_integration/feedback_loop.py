"""
Feedback Loop module for LLM integration.

This module provides functionality to improve code generation based on feedback.
"""

import os
import json
import time
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path
from rich.console import Console
from rich.panel import Panel

from .error_collector import ErrorCollector, ErrorInstance

console = Console()

class FeedbackEntry:
    """Represents a feedback entry."""
    
    def __init__(self, entry_id: str, component_path: str, feedback_type: str, 
                feedback_message: str, timestamp: float = None):
        """Initialize feedback entry.
        
        Args:
            entry_id: ID of the entry.
            component_path: Path to the component.
            feedback_type: Type of feedback (e.g., "error", "warning", "suggestion").
            feedback_message: Feedback message.
            timestamp: Timestamp of when the feedback was given.
        """
        self.entry_id = entry_id
        self.component_path = component_path
        self.feedback_type = feedback_type
        self.feedback_message = feedback_message
        self.timestamp = timestamp or time.time()
        self.resolved = False
        self.resolution = None
    
    def mark_resolved(self, resolution: str = None):
        """Mark the feedback as resolved.
        
        Args:
            resolution: Resolution message.
        """
        self.resolved = True
        self.resolution = resolution
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary.
        
        Returns:
            Dictionary representation of the feedback entry.
        """
        return {
            "entry_id": self.entry_id,
            "component_path": self.component_path,
            "feedback_type": self.feedback_type,
            "feedback_message": self.feedback_message,
            "timestamp": self.timestamp,
            "resolved": self.resolved,
            "resolution": self.resolution
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'FeedbackEntry':
        """Create from dictionary.
        
        Args:
            data: Dictionary representation of the feedback entry.
            
        Returns:
            FeedbackEntry instance.
        """
        entry = cls(
            entry_id=data["entry_id"],
            component_path=data["component_path"],
            feedback_type=data["feedback_type"],
            feedback_message=data["feedback_message"],
            timestamp=data.get("timestamp")
        )
        
        entry.resolved = data.get("resolved", False)
        entry.resolution = data.get("resolution")
        
        return entry


class FeedbackLoop:
    """Manages feedback for code generation."""
    
    def __init__(self, project_path: str, llm_client=None):
        """Initialize feedback loop.
        
        Args:
            project_path: Path to the project directory.
            llm_client: LLM client to use for generating improvements.
        """
        self.project_path = Path(project_path)
        self.llm_client = llm_client
        self.feedback_entries = {}  # type: Dict[str, FeedbackEntry]
        self.error_collector = ErrorCollector(project_path)
        
        # Create feedback directory if it doesn't exist
        feedback_dir = os.path.join(project_path, ".feedback")
        os.makedirs(feedback_dir, exist_ok=True)
    
    def add_feedback(self, component_path: str, feedback_type: str, 
                   feedback_message: str) -> str:
        """Add feedback.
        
        Args:
            component_path: Path to the component.
            feedback_type: Type of feedback (e.g., "error", "warning", "suggestion").
            feedback_message: Feedback message.
            
        Returns:
            ID of the added feedback entry.
        """
        import hashlib
        
        # Generate a unique ID for the feedback
        entry_id = hashlib.md5(f"{component_path}:{feedback_type}:{feedback_message}".encode()).hexdigest()[:8]
        
        # Create the feedback entry
        entry = FeedbackEntry(
            entry_id=entry_id,
            component_path=component_path,
            feedback_type=feedback_type,
            feedback_message=feedback_message
        )
        
        # Add the entry
        self.feedback_entries[entry_id] = entry
        
        # If the feedback is an error, add it to the error collector
        if feedback_type == "error":
            self.error_collector.add_error(
                error_message=feedback_message,
                file_path=component_path
            )
        
        # Save the feedback
        self._save_feedback()
        
        return entry_id
    
    def add_error_feedback(self, error: ErrorInstance) -> str:
        """Add feedback from an error.
        
        Args:
            error: Error instance.
            
        Returns:
            ID of the added feedback entry.
        """
        return self.add_feedback(
            component_path=error.file_path,
            feedback_type="error",
            feedback_message=error.error_message
        )
    
    def mark_resolved(self, entry_id: str, resolution: str = None) -> bool:
        """Mark a feedback entry as resolved.
        
        Args:
            entry_id: ID of the feedback entry.
            resolution: Resolution message.
            
        Returns:
            Whether the operation was successful.
        """
        entry = self.feedback_entries.get(entry_id)
        if not entry:
            return False
        
        entry.mark_resolved(resolution)
        
        # Save the feedback
        self._save_feedback()
        
        return True
    
    def get_feedback(self, entry_id: str) -> Optional[FeedbackEntry]:
        """Get a feedback entry by ID.
        
        Args:
            entry_id: ID of the feedback entry.
            
        Returns:
            Feedback entry or None if not found.
        """
        return self.feedback_entries.get(entry_id)
    
    def get_feedback_for_component(self, component_path: str) -> List[FeedbackEntry]:
        """Get feedback for a component.
        
        Args:
            component_path: Path to the component.
            
        Returns:
            List of feedback entries.
        """
        return [
            entry for entry in self.feedback_entries.values()
            if entry.component_path == component_path
        ]
    
    def get_unresolved_feedback(self) -> List[FeedbackEntry]:
        """Get unresolved feedback.
        
        Returns:
            List of unresolved feedback entries.
        """
        return [
            entry for entry in self.feedback_entries.values()
            if not entry.resolved
        ]
    
    def generate_improvement(self, component_path: str) -> Tuple[bool, str]:
        """Generate an improvement for a component based on feedback.
        
        Args:
            component_path: Path to the component.
            
        Returns:
            Tuple of (success, improved_code).
        """
        if not self.llm_client:
            console.print("[red]No LLM client provided for generating improvements[/red]")
            return False, ""
        
        # Get feedback for the component
        feedback = self.get_feedback_for_component(component_path)
        
        if not feedback:
            console.print(f"[yellow]No feedback found for component {component_path}[/yellow]")
            return False, ""
        
        # Get the current code
        full_path = os.path.join(self.project_path, component_path)
        
        try:
            with open(full_path, 'r') as f:
                current_code = f.read()
        except Exception as e:
            console.print(f"[red]Error reading component: {str(e)}[/red]")
            return False, ""
        
        # Create a prompt for improvement
        prompt = f"""
You are an expert software developer. Improve the following code based on the feedback provided:

Feedback:
{chr(10).join(f"- [{entry.feedback_type}] {entry.feedback_message}" for entry in feedback)}

Current code:
```
{current_code}
```

Return only the improved code without any explanations or markdown formatting.
"""
        
        # Generate improved code
        try:
            improved_code = self.llm_client.generate(prompt)
            
            # Extract the code from the LLM response (in case it includes explanations)
            import re
            code_match = re.search(r"```(?:\w+)?\n(.*?)```", improved_code, re.DOTALL)
            if code_match:
                improved_code = code_match.group(1)
            
            return True, improved_code
        except Exception as e:
            console.print(f"[red]Error generating improvement: {str(e)}[/red]")
            return False, ""
    
    def apply_improvement(self, component_path: str, improved_code: str) -> bool:
        """Apply an improvement to a component.
        
        Args:
            component_path: Path to the component.
            improved_code: Improved code.
            
        Returns:
            Whether the operation was successful.
        """
        full_path = os.path.join(self.project_path, component_path)
        
        try:
            # Create a backup of the original file
            backup_path = f"{full_path}.bak"
            with open(full_path, 'r') as src_file:
                with open(backup_path, 'w') as dst_file:
                    dst_file.write(src_file.read())
            
            # Write the improved code
            with open(full_path, 'w') as f:
                f.write(improved_code)
            
            # Mark feedback as resolved
            for entry in self.get_feedback_for_component(component_path):
                self.mark_resolved(entry.entry_id, "Applied automatic improvement")
            
            console.print(f"[green]Applied improvement to {component_path}[/green]")
            return True
        except Exception as e:
            console.print(f"[red]Error applying improvement: {str(e)}[/red]")
            return False
    
    def improve_component(self, component_path: str) -> bool:
        """Improve a component based on feedback.
        
        Args:
            component_path: Path to the component.
            
        Returns:
            Whether the operation was successful.
        """
        console.print(f"[cyan]Improving component {component_path}...[/cyan]")
        
        # Generate improvement
        success, improved_code = self.generate_improvement(component_path)
        
        if not success:
            return False
        
        # Apply improvement
        return self.apply_improvement(component_path, improved_code)
    
    def _save_feedback(self):
        """Save feedback to disk."""
        feedback_file = os.path.join(self.project_path, ".feedback", "feedback.json")
        
        try:
            data = {
                entry_id: entry.to_dict()
                for entry_id, entry in self.feedback_entries.items()
            }
            
            with open(feedback_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            console.print(f"[red]Error saving feedback: {str(e)}[/red]")
    
    def _load_feedback(self):
        """Load feedback from disk."""
        feedback_file = os.path.join(self.project_path, ".feedback", "feedback.json")
        
        if not os.path.exists(feedback_file):
            return
        
        try:
            with open(feedback_file, 'r') as f:
                data = json.load(f)
            
            self.feedback_entries = {
                entry_id: FeedbackEntry.from_dict(entry_data)
                for entry_id, entry_data in data.items()
            }
        except Exception as e:
            console.print(f"[red]Error loading feedback: {str(e)}[/red]")
    
    def generate_feedback_report(self) -> str:
        """Generate a report of feedback.
        
        Returns:
            Report as a string.
        """
        report = "# Feedback Report\n\n"
        
        # Group feedback by component
        feedback_by_component = {}
        for entry in self.feedback_entries.values():
            if entry.component_path not in feedback_by_component:
                feedback_by_component[entry.component_path] = []
            feedback_by_component[entry.component_path].append(entry)
        
        # Generate report for each component
        for component_path, entries in feedback_by_component.items():
            report += f"## {component_path}\n\n"
            
            # Group by feedback type
            entries_by_type = {}
            for entry in entries:
                if entry.feedback_type not in entries_by_type:
                    entries_by_type[entry.feedback_type] = []
                entries_by_type[entry.feedback_type].append(entry)
            
            # Generate report for each feedback type
            for feedback_type, type_entries in entries_by_type.items():
                report += f"### {feedback_type.capitalize()}\n\n"
                
                for entry in type_entries:
                    status = "✅ Resolved" if entry.resolved else "❌ Unresolved"
                    report += f"- [{status}] {entry.feedback_message}\n"
                    if entry.resolved and entry.resolution:
                        report += f"  - Resolution: {entry.resolution}\n"
                
                report += "\n"
        
        return report
