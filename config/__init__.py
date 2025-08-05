"""
Configuration management package for the CodeBase.

This package provides configuration management for the CodeBase,
including system settings, model configurations, logging setup,
and prompt templates.

Modules:
- system_config: System-wide configuration settings
- logging_config.yaml: Logging configuration in YAML format
- model_config.json: Model-specific configuration settings
- prompt_templates.yaml: Prompt template definitions

All configuration follows enterprise software standards with proper
validation, type safety, and comprehensive documentation.
"""

from . import system_config

__version__ = "1.0.0"
__author__ = "Anonymous"
__description__ = "Configuration management package for the CodeBase"
