"""
Tests for the error handling module.
"""

import pytest

from projects_tools.utils.errors import (
    ProjectsToolsError,
    ValidationError,
    APIError,
    format_error,
)


def test_projects_tools_error():
    """Test the base ProjectsToolsError."""
    error = ProjectsToolsError("Test error")
    assert str(error) == "Test error"
    assert error.message == "Test error"
    assert error.details == {}
    
    error_with_details = ProjectsToolsError("Test error", {"key": "value"})
    assert error_with_details.message == "Test error"
    assert error_with_details.details == {"key": "value"}


def test_validation_error():
    """Test ValidationError."""
    error = ValidationError("Validation failed")
    assert str(error) == "Validation failed"
    assert error.message == "Validation failed"
    assert error.errors == []
    assert error.details == {}
    
    error_with_errors = ValidationError(
        "Validation failed",
        ["Error 1", "Error 2"],
        {"key": "value"}
    )
    assert error_with_errors.message == "Validation failed"
    assert error_with_errors.errors == ["Error 1", "Error 2"]
    assert error_with_errors.details == {"key": "value"}


def test_api_error():
    """Test APIError."""
    error = APIError("API error")
    assert str(error) == "API error"
    assert error.message == "API error"
    assert error.status_code is None
    assert error.response == {}
    assert error.details == {}
    
    error_with_details = APIError(
        "API error",
        status_code=404,
        response={"error": "Not found"},
        details={"key": "value"}
    )
    assert error_with_details.message == "API error"
    assert error_with_details.status_code == 404
    assert error_with_details.response == {"error": "Not found"}
    assert error_with_details.details == {"key": "value"}


def test_format_error():
    """Test error formatting."""
    # Test formatting a ValidationError
    validation_error = ValidationError(
        "Validation failed",
        ["Error 1", "Error 2"]
    )
    formatted = format_error(validation_error)
    assert "Validation failed" in formatted
    assert "Error 1" in formatted
    assert "Error 2" in formatted
    
    # Test formatting an APIError
    api_error = APIError(
        "API error",
        status_code=404,
        response={"error": "Not found"}
    )
    formatted = format_error(api_error)
    assert "API error" in formatted
    assert "Status code: 404" in formatted
    assert "Not found" in formatted
    
    # Test formatting a ProjectsToolsError
    error = ProjectsToolsError(
        "Test error",
        {"key": "value"}
    )
    formatted = format_error(error)
    assert "Test error" in formatted
    assert "key: value" in formatted
    
    # Test formatting a standard Exception
    std_error = Exception("Standard error")
    formatted = format_error(std_error)
    assert formatted == "Standard error"
