"""
Validators for CLI input.

This module provides validators for CLI input.
"""

import os
import re
from pathlib import Path
from typing import List, Dict, Any, Optional, Union, Callable, TypeVar

from ..utils.errors import ValidationError

T = TypeVar("T")


def validate_project_name(name: str) -> str:
    """
    Validate a project name.

    Args:
        name: Project name to validate.

    Returns:
        Validated project name.

    Raises:
        ValidationError: If the project name is invalid.
    """
    if not name:
        raise ValidationError("Project name cannot be empty")
    
    if not re.match(r"^[a-zA-Z0-9_-]+$", name):
        raise ValidationError(
            "Project name can only contain letters, numbers, underscores, and hyphens"
        )
    
    if os.path.exists(name):
        raise ValidationError(
            f"Directory '{name}' already exists. Please choose a different name or delete the existing directory."
        )
    
    return name


def validate_project_path(path: str) -> Path:
    """
    Validate a project path.

    Args:
        path: Project path to validate.

    Returns:
        Validated project path.

    Raises:
        ValidationError: If the project path is invalid.
    """
    try:
        path_obj = Path(path)
        if not path_obj.exists():
            raise ValidationError(f"Path '{path}' does not exist")
        if not path_obj.is_dir():
            raise ValidationError(f"Path '{path}' is not a directory")
        return path_obj
    except Exception as e:
        if isinstance(e, ValidationError):
            raise
        raise ValidationError(f"Invalid path: {str(e)}")


def validate_component_path(path: str, project_path: Optional[str] = None) -> str:
    """
    Validate a component path.

    Args:
        path: Component path to validate.
        project_path: Optional project path for relative paths.

    Returns:
        Validated component path.

    Raises:
        ValidationError: If the component path is invalid.
    """
    try:
        if project_path:
            full_path = os.path.join(project_path, path)
        else:
            full_path = path
        
        if not os.path.exists(full_path):
            raise ValidationError(f"Component path '{path}' does not exist")
        if not os.path.isfile(full_path):
            raise ValidationError(f"Component path '{path}' is not a file")
        return path
    except Exception as e:
        if isinstance(e, ValidationError):
            raise
        raise ValidationError(f"Invalid component path: {str(e)}")


def validate_llm_provider(provider: str) -> str:
    """
    Validate an LLM provider.

    Args:
        provider: LLM provider to validate.

    Returns:
        Validated LLM provider.

    Raises:
        ValidationError: If the LLM provider is invalid.
    """
    valid_providers = ["openai", "anthropic"]
    if provider.lower() not in valid_providers:
        raise ValidationError(
            f"Invalid LLM provider: {provider}. Valid providers are: {', '.join(valid_providers)}"
        )
    return provider.lower()


def validate_frontend_type(frontend_type: str) -> str:
    """
    Validate a frontend type.

    Args:
        frontend_type: Frontend type to validate.

    Returns:
        Validated frontend type.

    Raises:
        ValidationError: If the frontend type is invalid.
    """
    valid_types = ["vue", "reactjs"]
    if frontend_type.lower() not in valid_types:
        raise ValidationError(
            f"Invalid frontend type: {frontend_type}. Valid types are: {', '.join(valid_types)}"
        )
    return frontend_type.lower()


def validate_db_type(db_type: str) -> str:
    """
    Validate a database type.

    Args:
        db_type: Database type to validate.

    Returns:
        Validated database type.

    Raises:
        ValidationError: If the database type is invalid.
    """
    valid_types = ["PostgreSQL", "MySQL", "SQLite"]
    if db_type not in valid_types:
        raise ValidationError(
            f"Invalid database type: {db_type}. Valid types are: {', '.join(valid_types)}"
        )
    return db_type


def validate_feedback_type(feedback_type: str) -> str:
    """
    Validate a feedback type.

    Args:
        feedback_type: Feedback type to validate.

    Returns:
        Validated feedback type.

    Raises:
        ValidationError: If the feedback type is invalid.
    """
    valid_types = ["error", "warning", "suggestion", "issue"]
    if feedback_type.lower() not in valid_types:
        raise ValidationError(
            f"Invalid feedback type: {feedback_type}. Valid types are: {', '.join(valid_types)}"
        )
    return feedback_type.lower()


def validate_optional(
    validator: Callable[[T], T], allow_none: bool = True
) -> Callable[[Optional[T]], Optional[T]]:
    """
    Create a validator that allows None values.

    Args:
        validator: Validator function.
        allow_none: Whether to allow None values.

    Returns:
        Validator function that allows None values.
    """
    def optional_validator(value: Optional[T]) -> Optional[T]:
        if value is None and allow_none:
            return None
        return validator(value)
    
    return optional_validator


def validate_list(
    validator: Callable[[T], T], allow_empty: bool = True
) -> Callable[[List[T]], List[T]]:
    """
    Create a validator for lists.

    Args:
        validator: Validator function for list items.
        allow_empty: Whether to allow empty lists.

    Returns:
        Validator function for lists.
    """
    def list_validator(values: List[T]) -> List[T]:
        if not values and not allow_empty:
            raise ValidationError("List cannot be empty")
        return [validator(value) for value in values]
    
    return list_validator
