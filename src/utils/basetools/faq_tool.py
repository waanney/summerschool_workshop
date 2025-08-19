"""
FAQ search and retrieval module.

This module provides functionality for searching and retrieving FAQ entries from
a Milvus vector database using semantic similarity search. It supports both
question and answer search modes with configurable result limits.
"""

from typing import List, Dict
from enum import Enum

from pydantic import BaseModel, Field

from data.embeddings.embedding_engine import EmbeddingEngine
from data.milvus.milvus_client import MilvusClient


class SearchMode(str, Enum):
    """Enum for search modes."""

    QUESTIONS_ONLY = "questions_only"
    ANSWERS_ONLY = "answers_only"
    HYBRID = "hybrid"


class SearchInput(BaseModel):
    """Input model for FAQ search requests."""

    query: str = Field(..., description="Search query text")
    limit: int = Field(3, description="Number of top results to return")
    search_answers: bool = Field(
        False, description="Whether to search in answer embeddings"
    )


class FAQResult(BaseModel):
    """Model for individual FAQ search results."""

    question: str = Field(..., description="The FAQ question")
    answer: str = Field(..., description="The FAQ answer")
    similarity_score: float = Field(..., description="Similarity score for the result")
    source: str = Field(default="", description="Source of the FAQ entry")


class SearchOutput(BaseModel):
    """Output model for FAQ search results."""

    results: List[FAQResult] = Field(..., description="List of FAQ search results")
    total_results: int = Field(..., description="Total number of results found")
    query: str = Field(..., description="The original search query")


# Global embedding engine instance
embedding_engine: EmbeddingEngine = EmbeddingEngine()


def faq_tool(
    input: SearchInput, collection_name: str = "database"
) -> SearchOutput:
    """
    Search FAQ entries using semantic similarity.

    This function performs a semantic search on FAQ entries stored in Milvus.
    It can search in questions, answers, or both depending on the configuration.

    Args:
        input: SearchInput object containing query and search parameters
        collection_name: Name of the Milvus collection to search in

    Returns:
        SearchOutput: Object containing search results and metadata

    Raises:
        ConnectionError: If unable to connect to Milvus
        ValueError: If query is empty or invalid
        Exception: For any other search errors
    """
    client: MilvusClient = MilvusClient(collection_name=collection_name)

    query_embedding: List[float] = embedding_engine.get_query_embedding(input.query)

    raw_results: List[Dict[str, str | float]] = client.hybrid_search(
        query_text=input.query,
        query_dense_embedding=query_embedding,
        limit=input.limit,
        search_answers=input.search_answers,
    )

    # Convert raw results to structured FAQResult objects
    faq_results: List[FAQResult] = []
    for result in raw_results:
        faq_result: FAQResult = FAQResult(
            question=str(result.get("question", "")),
            answer=str(result.get("answer", "")),
            similarity_score=float(result.get("similarity_score", 0.0)),
            source=str(result.get("source", "")),
        )
        faq_results.append(faq_result)

    return SearchOutput(
        results=faq_results, total_results=len(faq_results), query=input.query
    )


def create_faq_tool(collection_name: str = "database") -> callable:
    """
    Create a FAQ tool function with a pre-configured collection name.

    This factory function creates a configured FAQ search function that uses
    a specific Milvus collection. The collection name is fixed and cannot be
    changed by the calling code.

    Args:
        collection_name: Name of the Milvus collection to use for searches

    Returns:
        callable: A function that performs FAQ searches using the specified collection

    Example:
        >>> faq_search = create_faq_tool("my_faq_collection")
        >>> result = faq_search(SearchInput(query="How to reset password?"))
    """

    def configured_faq_tool(input: SearchInput) -> SearchOutput:
        """
        Configured FAQ search function with fixed collection name.

        Args:
            input: SearchInput object containing query and search parameters

        Returns:
            SearchOutput: Object containing search results and metadata
        """
        return faq_tool(input, collection_name=collection_name)

    return configured_faq_tool
