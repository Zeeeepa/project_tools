"""
LLM Client module for Project Tools.

This module provides a unified interface to interact with various LLM providers.
"""

import os
import json
import requests
from typing import Dict, List, Optional, Union, Any
from abc import ABC, abstractmethod
from rich.console import Console

console = Console()

class LLMClient(ABC):
    """Abstract base class for LLM clients."""
    
    @abstractmethod
    def generate(self, prompt: str, **kwargs) -> str:
        """Generate text from a prompt."""
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """Check if the LLM service is available."""
        pass


class OpenAIClient(LLMClient):
    """Client for OpenAI API."""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4"):
        """Initialize OpenAI client.
        
        Args:
            api_key: OpenAI API key. If None, will try to get from environment.
            model: Model to use for generation.
        """
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY")
        self.model = model
        self.api_url = "https://api.openai.com/v1/chat/completions"
        
    def is_available(self) -> bool:
        """Check if OpenAI API is available."""
        return self.api_key is not None
    
    def generate(self, prompt: str, temperature: float = 0.7, max_tokens: int = 1000, **kwargs) -> str:
        """Generate text using OpenAI API.
        
        Args:
            prompt: The prompt to generate from.
            temperature: Controls randomness. Lower is more deterministic.
            max_tokens: Maximum number of tokens to generate.
            
        Returns:
            Generated text.
        """
        if not self.is_available():
            console.print("[red]OpenAI API key not found. Please set OPENAI_API_KEY environment variable.[/red]")
            return ""
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        data = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": temperature,
            "max_tokens": max_tokens,
            **kwargs
        }
        
        try:
            response = requests.post(self.api_url, headers=headers, json=data)
            response.raise_for_status()
            result = response.json()
            return result["choices"][0]["message"]["content"]
        except Exception as e:
            console.print(f"[red]Error calling OpenAI API: {str(e)}[/red]")
            return ""


class AnthropicClient(LLMClient):
    """Client for Anthropic API."""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "claude-3-opus-20240229"):
        """Initialize Anthropic client.
        
        Args:
            api_key: Anthropic API key. If None, will try to get from environment.
            model: Model to use for generation.
        """
        self.api_key = api_key or os.environ.get("ANTHROPIC_API_KEY")
        self.model = model
        self.api_url = "https://api.anthropic.com/v1/messages"
        
    def is_available(self) -> bool:
        """Check if Anthropic API is available."""
        return self.api_key is not None
    
    def generate(self, prompt: str, temperature: float = 0.7, max_tokens: int = 1000, **kwargs) -> str:
        """Generate text using Anthropic API.
        
        Args:
            prompt: The prompt to generate from.
            temperature: Controls randomness. Lower is more deterministic.
            max_tokens: Maximum number of tokens to generate.
            
        Returns:
            Generated text.
        """
        if not self.is_available():
            console.print("[red]Anthropic API key not found. Please set ANTHROPIC_API_KEY environment variable.[/red]")
            return ""
        
        headers = {
            "Content-Type": "application/json",
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01"
        }
        
        data = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": temperature,
            "max_tokens": max_tokens,
            **kwargs
        }
        
        try:
            response = requests.post(self.api_url, headers=headers, json=data)
            response.raise_for_status()
            result = response.json()
            return result["content"][0]["text"]
        except Exception as e:
            console.print(f"[red]Error calling Anthropic API: {str(e)}[/red]")
            return ""


def get_llm_client(provider: str = "openai", **kwargs) -> LLMClient:
    """Factory function to get an LLM client.
    
    Args:
        provider: The LLM provider to use. One of "openai" or "anthropic".
        **kwargs: Additional arguments to pass to the client constructor.
        
    Returns:
        An LLM client instance.
    """
    providers = {
        "openai": OpenAIClient,
        "anthropic": AnthropicClient
    }
    
    if provider not in providers:
        console.print(f"[red]Unknown provider: {provider}. Using OpenAI as default.[/red]")
        provider = "openai"
        
    return providers[provider](**kwargs)
