"""
Summerschool Workshop Source Package.

This is the main source package for the summerschool workshop project.
It contains all the core modules and functionality for the workshop
including data management, utilities, LLM integration, and more.

Packages:
- data: Data management and processing modules
- utils: Utility tools and helper functions
- llm: Large Language Model integration
- handlers: Error handling and request processing
- prompt_engineering: Prompt management and optimization
- mcp_tools: Model Context Protocol tools

All modules follow enterprise software standards with:
- Strong typing with no use of 'Any' types
- Comprehensive docstrings for all functions and classes
- Enum-based configuration for better type safety
- Structured input/output models using Pydantic
- Proper error handling and status reporting
- Multilingual language support where applicable

Usage:
    from src.utils.basetools import classification_tool
    from src.data.embeddings import EmbeddingEngine
    from src.llm.base import LLMBase
"""

from . import data
from . import utils
from . import llm
from . import handlers
from . import prompt_engineering
from . import mcp_tools

__version__ = "1.0.0"
__author__ = "Summerschool Workshop Team"
__description__ = "Main source package for the summerschool workshop project"
