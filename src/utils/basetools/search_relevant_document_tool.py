"""
Relevant document search and retrieval module.

This module provides functionality for searching and retrieving relevant document
chunks from a vector database using semantic similarity. It serves as a core
component in Retrieval-Augmented Generation (RAG) systems by fetching contextually
relevant text passages based on user queries.
"""

from typing import List, Dict
from enum import Enum

from pydantic import BaseModel, Field

from data.embeddings.embedding_engine import EmbeddingEngine
from data.milvus.milvus_client import MilvusClient


class SearchStatus(str, Enum):
    """Enum for search operation status."""

    SUCCESS = "success"
    NO_RESULTS = "no_results"
    BELOW_THRESHOLD = "below_threshold"
    ERROR = "error"


class SearchRelevantDocumentInput(BaseModel):
    """Input model for relevant document search operations."""

    user_query: str = Field(
        ..., description="The user's query to search for relevant documents"
    )
    k: int = Field(3, description="The maximum number of documents to return")
    threshold: float = Field(
        0.7,
        description="The minimum similarity score for a document to be considered relevant",
    )
    collection_name: str = Field(
        "database",
        description="The name of the Milvus collection to search in",
    )


class DocumentResult(BaseModel):
    """Model for individual document search results."""

    text: str = Field(..., description="The document text content")
    score: float = Field(..., description="Similarity score for the document")
    source: str = Field(default="", description="Source of the document")


class SearchRelevantDocumentOutput(BaseModel):
    """Output model for relevant document search operations."""

    documents: List[DocumentResult] = Field(
        ...,
        description="List of relevant document chunks retrieved from the vector database",
    )
    total_found: int = Field(..., description="Total number of documents found")
    query: str = Field(..., description="The original user query")
    status: SearchStatus = Field(
        SearchStatus.SUCCESS, description="Status of the search operation"
    )


# Global embedding engine instance
embedding_engine: EmbeddingEngine = EmbeddingEngine()


def search_relevant_document(
    input: SearchRelevantDocumentInput,
) -> SearchRelevantDocumentOutput:
    """
    Search for relevant document chunks based on a user query.

    This function serves as a core retrieval component in a Retrieval-Augmented
    Generation (RAG) system by fetching relevant document passages from a vector
    database. It differs from FAQ tools by retrieving raw text chunks rather
    than pre-defined question-answer pairs.

    Args:
        input: SearchRelevantDocumentInput object containing search parameters

    Returns:
        SearchRelevantDocumentOutput: Object containing relevant documents and metadata

    Raises:
        ConnectionError: If unable to connect to Milvus
        ValueError: If query is empty or invalid
        Exception: For any other search errors
    """
    try:
        client: MilvusClient = MilvusClient(collection_name=input.collection_name)

        query_embedding: List[float] = embedding_engine.get_query_embedding(
            input.user_query
        )

        search_results: List[Dict[str, str | float]] = client.generic_hybrid_search(
            query_dense_embedding=query_embedding,
            limit=input.k,
            query_text=input.user_query,
        )

        relevant_documents: List[DocumentResult] = []
        for result in search_results:
            score: float = float(result.get("score", 0.0))
            if score >= input.threshold:
                document_result: DocumentResult = DocumentResult(
                    text=str(result.get("text", "")),
                    score=score,
                    source=str(result.get("source", "")),
                )
                relevant_documents.append(document_result)

        status: SearchStatus = _determine_search_status(
            relevant_documents, input.threshold
        )

        return SearchRelevantDocumentOutput(
            documents=relevant_documents,
            total_found=len(relevant_documents),
            query=input.user_query,
            status=status,
        )

    except Exception as e:
        return SearchRelevantDocumentOutput(
            documents=[],
            total_found=0,
            query=input.user_query,
            status=SearchStatus.ERROR,
        )


def _determine_search_status(
    documents: List[DocumentResult], threshold: float
) -> SearchStatus:
    """
    Determine the status of the search operation based on results.

    Args:
        documents: List of found document results
        threshold: Minimum similarity threshold used

    Returns:
        SearchStatus: Status indicating the search outcome
    """
    if not documents:
        return SearchStatus.NO_RESULTS
    elif all(doc.score < threshold for doc in documents):
        return SearchStatus.BELOW_THRESHOLD
    else:
        return SearchStatus.SUCCESS
