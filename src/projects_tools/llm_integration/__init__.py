"""
LLM integration package for project_tools.

This package provides functionality for LLM-assisted project generation.
"""

from .project_genie import ProjectGenie
from .llm_client import LLMClient, get_llm_client
from .context_manager import ProjectContext
from .code_generator import CodeGenerator
from .validator import CodeValidator, ValidationResult
from .runtime_validator import RuntimeValidator, RuntimeValidationResult
from .db_schema_generator import DBSchemaGenerator
from .test_generator import TestGenerator
from .codebase_analyzer import CodebaseAnalyzer, DependencyGraph, CodeMetrics
from .error_collector import ErrorCollector, ErrorPattern, ErrorInstance
from .feedback_loop import FeedbackLoop, FeedbackEntry

__all__ = [
    'ProjectGenie',
    'LLMClient',
    'get_llm_client',
    'ProjectContext',
    'CodeGenerator',
    'CodeValidator',
    'ValidationResult',
    'RuntimeValidator',
    'RuntimeValidationResult',
    'DBSchemaGenerator',
    'TestGenerator',
    'CodebaseAnalyzer',
    'DependencyGraph',
    'CodeMetrics',
    'ErrorCollector',
    'ErrorPattern',
    'ErrorInstance',
    'FeedbackLoop',
    'FeedbackEntry'
]
