"""
Text embedding generation and management module.

This module provides functionality for generating text embeddings using
Sentence-Transformers models. It supports batch processing, query embedding,
and state management for embedding operations.
"""

from typing import List, Optional
from enum import Enum
import logging

from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logger: logging.Logger = logging.getLogger(__name__)


class EmbeddingModel(str, Enum):
    """Enum for supported embedding models."""
    MINI_LM_L6_V2 = "all-MiniLM-L6-v2"
    MULTILINGUAL_MINI_LM_L12_V2 = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"


class EmbeddingStatus(str, Enum):
    """Enum for embedding operation status."""
    SUCCESS = "success"
    FAILED = "failed"
    EMPTY_TEXT = "empty_text"
    MODEL_ERROR = "model_error"


class EmbeddingEngine:
    """
    A class that wraps the functionality for generating embeddings using Sentence-Transformers.
    
    This class provides methods for generating embeddings from text using various
    pre-trained models. It supports both single text and batch processing with
    proper error handling and logging.
    
    Attributes:
        model: The SentenceTransformer model instance
        model_name: Name of the loaded model
        corpus: List of corpus texts
        corpus_embeddings: Pre-computed embeddings for corpus texts
        save_path: Path for saving/loading embedding state
    """

    def __init__(
        self,
        model_name: EmbeddingModel = EmbeddingModel.MINI_LM_L6_V2,
        save_path: str = "embedding_state.json",
    ) -> None:
        """
        Initialize the EmbeddingEngine.

        Args:
            model_name: The name of the Sentence-Transformers model to use
            save_path: The path to the file where the embedding state will be saved/loaded
            
        Raises:
            ValueError: If model_name is invalid
            Exception: If model loading fails
        """
        try:
            # Initialize the Sentence-Transformer model
            self.model: SentenceTransformer = SentenceTransformer(model_name.value)
            self.model_name: str = model_name.value
            self.corpus: List[str] = []
            self.corpus_embeddings: Optional[List[List[float]]] = None
            self.save_path: str = save_path
            
            logger.info(f"EmbeddingEngine initialized with model: {model_name.value}")
            
        except Exception as e:
            logger.error(f"Failed to initialize EmbeddingEngine with model {model_name.value}: {e}")
            raise

    def get_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for a list of texts.
        
        This method processes a list of texts and generates embeddings for each one.
        It handles errors gracefully and logs warnings for failed embeddings.

        Args:
            texts: A list of text strings to embed

        Returns:
            List[List[float]]: A list of embeddings (list of floats) corresponding to each text
            
        Raises:
            ValueError: If texts list is empty or contains invalid items
        """
        if not texts:
            logger.warning("Empty texts list provided to get_embeddings")
            return []
        
        embeddings: List[List[float]] = []
        for i, text in enumerate(texts):
            if not isinstance(text, str) or not text.strip():
                logger.warning(f"Invalid text at index {i}: {text}")
                continue
                
            embedding: List[float] = self._generate_embedding(text)
            if embedding:
                embeddings.append(embedding)
            else:
                logger.warning(f"Embedding generation failed for text at index {i}: '{text[:50]}...'")
                
        return embeddings

    def get_query_embedding(self, query: str) -> List[float]:
        """
        Generate an embedding for a query string.
        
        This method is optimized for single query embedding generation,
        typically used in search and retrieval operations.

        Args:
            query: A query string to embed

        Returns:
            List[float]: The embedding vector of the query
            
        Raises:
            ValueError: If query is empty or invalid
        """
        if not query or not query.strip():
            logger.warning("Empty or invalid query provided to get_query_embedding")
            return []
            
        return self._generate_embedding(query)

    def _generate_embedding(self, text: str) -> List[float]:
        """
        Generate an embedding using Sentence-Transformers for a given text.
        
        This is the core method that handles the actual embedding generation.
        It includes proper error handling and logging.

        Args:
            text: A single text string to embed

        Returns:
            List[float]: A list of floats representing the text's embedding, or empty list if an error occurs
            
        Raises:
            Exception: If embedding generation fails
        """
        try:
            if not text or not text.strip():
                logger.warning("Empty text provided to _generate_embedding")
                return []
                
            # Generate embedding using Sentence-Transformers
            embedding = self.model.encode(text)
            # Convert the embedding from a NumPy array to a list of floats
            result: List[float] = embedding.tolist()
            
            logger.debug(f"Successfully generated embedding for text: '{text[:50]}...'")
            return result
            
        except Exception as e:
            logger.error(f"Error generating embedding for text: '{text[:50]}...'. Error: {e}")
            return []

    def get_model_info(self) -> dict[str, str | int]:
        """
        Get information about the loaded model.
        
        Returns:
            dict[str, str | int]: Dictionary containing model information
        """
        return {
            "model_name": self.model_name,
            "embedding_dimension": len(self.get_query_embedding("test")) if self.model else 0,
            "save_path": self.save_path,
        }
