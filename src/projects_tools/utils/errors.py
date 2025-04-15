"""
Error handling for projects_tools.

This module provides a custom exception hierarchy for projects_tools.
"""

from typing import Optional, List, Dict, Any


class ProjectsToolsError(Exception):
    """Base exception for all projects_tools errors."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        """
        Initialize the exception.

        Args:
            message: Error message.
            details: Additional details about the error.
        """
        self.message = message
        self.details = details or {}
        super().__init__(message)


class ConfigurationError(ProjectsToolsError):
    """Error related to configuration."""

    pass


class ValidationError(ProjectsToolsError):
    """Error related to validation."""

    def __init__(
        self, message: str, errors: Optional[List[str]] = None, details: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize the exception.

        Args:
            message: Error message.
            errors: List of validation errors.
            details: Additional details about the error.
        """
        self.errors = errors or []
        super().__init__(message, details)


class ProjectCreationError(ProjectsToolsError):
    """Error related to project creation."""

    pass


class TemplateError(ProjectsToolsError):
    """Error related to templates."""

    pass


class LLMError(ProjectsToolsError):
    """Error related to LLM integration."""

    pass


class APIError(LLMError):
    """Error related to API calls."""

    def __init__(
        self,
        message: str,
        status_code: Optional[int] = None,
        response: Optional[Dict[str, Any]] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialize the exception.

        Args:
            message: Error message.
            status_code: HTTP status code.
            response: API response.
            details: Additional details about the error.
        """
        self.status_code = status_code
        self.response = response or {}
        super().__init__(message, details)


class AuthenticationError(APIError):
    """Error related to authentication."""

    pass


class RateLimitError(APIError):
    """Error related to rate limiting."""

    pass


class CodeGenerationError(LLMError):
    """Error related to code generation."""

    pass


class CodeAnalysisError(LLMError):
    """Error related to code analysis."""

    pass


class RuntimeError(ProjectsToolsError):
    """Error related to runtime execution."""

    pass


class CommandError(ProjectsToolsError):
    """Error related to command execution."""

    pass


def format_error(error: Exception) -> str:
    """
    Format an exception for display.

    Args:
        error: Exception to format.

    Returns:
        Formatted error message.
    """
    if isinstance(error, ValidationError):
        message = f"{error.message}\n"
        if error.errors:
            message += "\nValidation errors:\n"
            for i, err in enumerate(error.errors, 1):
                message += f"  {i}. {err}\n"
        return message
    elif isinstance(error, APIError):
        message = f"{error.message}\n"
        if error.status_code:
            message += f"\nStatus code: {error.status_code}\n"
        if error.response:
            message += "\nResponse:\n"
            for key, value in error.response.items():
                message += f"  {key}: {value}\n"
        return message
    elif isinstance(error, ProjectsToolsError):
        message = f"{error.message}\n"
        if error.details:
            message += "\nDetails:\n"
            for key, value in error.details.items():
                message += f"  {key}: {value}\n"
        return message
    else:
        return str(error)
