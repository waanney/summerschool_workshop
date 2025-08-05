"""
Data management and processing package for the CodeBase.

This package provides modules for handling various types of data operations
including embeddings, vector storage, caching, and prompt management.

Modules:
- embeddings: Text embedding generation and management
- milvus: Vector database operations and indexing
- cache: Caching mechanisms for improved performance
- prompts: Prompt templates and management
- mock_data: Sample data for testing and development

All modules follow enterprise software standards with strong typing,
comprehensive documentation, and proper error handling.
"""

from . import embeddings
from . import milvus
from . import cache
from . import prompts
from . import mock_data

__version__ = "1.0.0"
__author__ = "Anonymous"
__description__ = (
    "Data management and processing package for the CodeBase"
)
