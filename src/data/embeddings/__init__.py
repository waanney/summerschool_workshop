"""
Text embedding generation and management package.

This package provides functionality for generating and managing text embeddings
using various pre-trained models. It supports both single text and batch processing
with proper error handling and logging.

Modules:
- embedding_engine: Core embedding generation using Sentence-Transformers

All modules follow enterprise software standards with strong typing,
comprehensive documentation, and proper error handling.
"""

from .embedding_engine import (
    EmbeddingEngine,
    EmbeddingModel,
    EmbeddingStatus,
)

__version__ = "1.0.0"
__author__ = "Summerschool Workshop Team"
__description__ = "Text embedding generation and management package"
