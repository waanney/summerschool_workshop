"""
System configuration management module.

This module provides centralized configuration management for the codebase.
It handles environment variables, application settings,
and provides type-safe access to configuration values.
"""

from datetime import datetime
from zoneinfo import ZoneInfo
import os
from typing import Optional
from enum import Enum

from dotenv import load_dotenv


class LogLevel(str, Enum):
    """Enum for log levels."""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class Environment(str, Enum):
    """Enum for environment types."""
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"


class Settings:
    """
    Settings for the CodeBase.
    
    This class manages all configuration settings for the application,
    including environment variables, API settings, database connections,
    and logging configuration. It provides type-safe access to all
    configuration values with proper defaults.
    
    Attributes:
        APP_NAME: Application name
        DEBUG: Debug mode flag
        API_VERSION: API version string
        HOST: API host address
        PORT: API port number
        TIMEZONE: Application timezone
        MILVUS_URL: Milvus database URL
        MILVUS_TOKEN: Milvus authentication token
        OPENAI_API_KEY: OpenAI API key
        LOG_LEVEL: Logging level
        LOG_FORMAT: Log message format
        LOG_FILE: Log file path
        RATE_LIMIT_PER_MINUTE: Rate limiting configuration
    """

    def __init__(self) -> None:
        """
        Initialize the Settings class.
        
        This method loads environment variables from a .env file and
        sets up all configuration values with proper type conversion
        and validation.
        
        Raises:
            ValueError: If required environment variables are missing
            TypeError: If environment variable type conversion fails
        """
        # Load environment variables from .env file first
        env_file: str = os.getenv("ENVIRONMENT_FILE", ".env")
        load_dotenv(env_file)
        
        # Application settings
        self.APP_NAME: str = "CodeBase"
        self.DEBUG: bool = self._get_bool_env("DEBUG", True)
        self.API_VERSION: str = "v1"
        self.HOST: str = os.getenv("API_HOST", "127.0.0.1")
        self.PORT: int = self._get_int_env("API_PORT", 7000)
        self.TIMEZONE: str = os.getenv("TIMEZONE", "UTC")
        
        # Environment
        self.ENVIRONMENT: Environment = self._get_environment()

        # Milvus settings
        self.MILVUS_URL: Optional[str] = os.getenv("MILVUS_URI")
        self.MILVUS_TOKEN: Optional[str] = os.getenv("MILVUS_TOKEN")

        # Model serving settings
        self.OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")

        # Logging settings
        self.LOG_LEVEL: LogLevel = self._get_log_level()
        self.LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        self.LOG_FILE: str = os.getenv("LOG_FILE", "logs/workshop.log")

        # Rate limiting
        self.RATE_LIMIT_PER_MINUTE: int = self._get_int_env("RATE_LIMIT_PER_MINUTE", 60)

    def _get_bool_env(self, key: str, default: bool) -> bool:
        """
        Get boolean environment variable with proper conversion.
        
        Args:
            key: Environment variable key
            default: Default value if not found
            
        Returns:
            bool: Boolean value from environment variable
        """
        value: Optional[str] = os.getenv(key)
        if value is None:
            return default
        return value.lower() in ("true", "1", "yes", "on")

    def _get_int_env(self, key: str, default: int) -> int:
        """
        Get integer environment variable with proper conversion.
        
        Args:
            key: Environment variable key
            default: Default value if not found
            
        Returns:
            int: Integer value from environment variable
            
        Raises:
            ValueError: If environment variable cannot be converted to int
        """
        value: Optional[str] = os.getenv(key)
        if value is None:
            return default
        try:
            return int(value)
        except ValueError as e:
            raise ValueError(f"Environment variable {key} must be an integer: {e}")

    def _get_environment(self) -> Environment:
        """
        Get current environment from environment variable.
        
        Returns:
            Environment: Current environment enum value
        """
        env_str: str = os.getenv("ENVIRONMENT", "development").lower()
        try:
            return Environment(env_str)
        except ValueError:
            return Environment.DEVELOPMENT

    def _get_log_level(self) -> LogLevel:
        """
        Get log level from environment variable.
        
        Returns:
            LogLevel: Log level enum value
        """
        level_str: str = os.getenv("LOG_LEVEL", "INFO").upper()
        try:
            return LogLevel(level_str)
        except ValueError:
            return LogLevel.INFO

    def get_current_time(self) -> datetime:
        """
        Get the current time in the specified timezone.
        
        Returns:
            datetime: Current datetime in the configured timezone
        """
        return datetime.now(ZoneInfo(self.TIMEZONE))

    def get_config_summary(self) -> dict[str, str | int | bool]:
        """
        Get a summary of current configuration settings.
        
        Returns:
            dict[str, str | int | bool]: Dictionary containing configuration summary
        """
        return {
            "app_name": self.APP_NAME,
            "debug": self.DEBUG,
            "api_version": self.API_VERSION,
            "host": self.HOST,
            "port": self.PORT,
            "timezone": self.TIMEZONE,
            "environment": self.ENVIRONMENT.value,
            "log_level": self.LOG_LEVEL.value,
            "rate_limit": self.RATE_LIMIT_PER_MINUTE,
        }


# Global settings instance
settings: Settings = Settings()
