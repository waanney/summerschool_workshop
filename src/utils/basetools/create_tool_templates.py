"""
Tool creation templates and examples module.

This module provides templates and examples for creating new tools following
the established patterns in the codebase. It demonstrates proper structure,
typing, and documentation standards for tool development.
"""

# *********************
# 1. Import libraries and modules
# *********************

# from typing import List, Dict, Optional
# from enum import Enum
# from pydantic import BaseModel, Field
# from data.embeddings.embedding_engine import EmbeddingEngine
# from data.milvus.milvus_client import MilvusClient


# ***********************
# 2. Initialize global instances if needed
# ***********************

# embedding_engine: EmbeddingEngine = EmbeddingEngine()


# *********************
# 3. Define enums for strong typing
# *********************

# class SearchMode(str, Enum):
#     """Enum for search modes."""
#     SEMANTIC = "semantic"
#     KEYWORD = "keyword"
#     HYBRID = "hybrid"


# class SearchStatus(str, Enum):
#     """Enum for search operation status."""
#     SUCCESS = "success"
#     NO_RESULTS = "no_results"
#     ERROR = "error"


# *********************
# 4. Configure input models
# *********************

# class SearchRelevantDocumentInput(BaseModel):
#     """Input model for document search operations."""
#
#     user_query: str = Field(..., description="The user's query to search for relevant documents")
#     k: int = Field(3, description="The maximum number of documents to return")
#     threshold: float = Field(0.7, description="The minimum similarity score for a document to be considered relevant")
#     collection_name: str = Field("database", description="The name of the Milvus collection to search in")
#     search_mode: SearchMode = Field(SearchMode.SEMANTIC, description="Search mode to use")


# *********************
# 5. Configure output models
# *********************

# class DocumentResult(BaseModel):
#     """Model for individual document search results."""
#
#     text: str = Field(..., description="The document text content")
#     score: float = Field(..., description="Similarity score for the document")
#     source: str = Field(default="", description="Source of the document")


# class SearchRelevantDocumentOutput(BaseModel):
#     """Output model for document search operations."""
#
#     documents: List[DocumentResult] = Field(..., description="List of relevant document chunks retrieved from the vector database")
#     total_found: int = Field(..., description="Total number of documents found")
#     query: str = Field(..., description="The original user query")
#     status: SearchStatus = Field(SearchStatus.SUCCESS, description="Status of the search operation")


# **********************
# 6. Create main tool function
# **********************

# def search_relevant_document(input: SearchRelevantDocumentInput) -> SearchRelevantDocumentOutput:
#     """
#     Search for relevant document chunks based on a user query.
#
#     This function serves as a core retrieval component in a Retrieval-Augmented
#     Generation (RAG) system by fetching relevant document passages from a vector
#     database. It differs from FAQ tools by retrieving raw text chunks rather
#     than pre-defined question-answer pairs.
#
#     Args:
#         input: SearchRelevantDocumentInput object containing search parameters
#
#     Returns:
#         SearchRelevantDocumentOutput: Object containing relevant documents and metadata
#
#     Raises:
#         ConnectionError: If unable to connect to Milvus
#         ValueError: If query is empty or invalid
#         Exception: For any other search errors
#     """
#     try:
#         client: MilvusClient = MilvusClient(collection_name=input.collection_name)
#
#         query_embedding: List[float] = embedding_engine.get_query_embedding(input.user_query)
#
#         search_results: List[Dict[str, str | float]] = client.generic_hybrid_search(
#             query_dense_embedding=query_embedding,
#             limit=input.k,
#             query_text=input.user_query
#         )
#
#         relevant_documents: List[DocumentResult] = []
#         for result in search_results:
#             score: float = float(result.get('score', 0.0))
#             if score >= input.threshold:
#                 document_result: DocumentResult = DocumentResult(
#                     text=str(result.get('text', '')),
#                     score=score,
#                     source=str(result.get('source', ''))
#                 )
#                 relevant_documents.append(document_result)
#
#         return SearchRelevantDocumentOutput(
#             documents=relevant_documents,
#             total_found=len(relevant_documents),
#             query=input.user_query,
#             status=SearchStatus.SUCCESS if relevant_documents else SearchStatus.NO_RESULTS
#         )
#
#     except Exception as e:
#         return SearchRelevantDocumentOutput(
#             documents=[],
#             total_found=0,
#             query=input.user_query,
#             status=SearchStatus.ERROR
#         )


# **********************
# 7. Create helper functions (optional)
# **********************

# def _validate_search_parameters(input: SearchRelevantDocumentInput) -> bool:
#     """
#     Validate search input parameters.
#
#     Args:
#         input: Search input parameters to validate
#
#     Returns:
#         bool: True if parameters are valid, False otherwise
#     """
#     if not input.user_query or not input.user_query.strip():
#         return False
#     if input.k <= 0 or input.k > 100:
#         return False
#     if input.threshold < 0.0 or input.threshold > 1.0:
#         return False
#     return True


# **********************
# 8. Create factory function (optional)
# **********************

# def create_search_tool(collection_name: str = "database") -> callable:
#     """
#     Create a search tool function with a pre-configured collection name.
#
#     This factory function creates a configured search function that uses
#     a specific Milvus collection. The collection name is fixed and cannot
#     be changed by the calling code.
#
#     Args:
#         collection_name: Name of the Milvus collection to use for searches
#
#     Returns:
#         callable: A function that performs searches using the specified collection
#     """
#     def configured_search_tool(input: SearchRelevantDocumentInput) -> SearchRelevantDocumentOutput:
#         """
#         Configured search function with fixed collection name.
#
#         Args:
#             input: SearchRelevantDocumentInput object containing search parameters
#
#         Returns:
#             SearchRelevantDocumentOutput: Object containing search results and metadata
#         """
#         # Override collection name with the fixed one
#         input.collection_name = collection_name
#         return search_relevant_document(input)
#
#     return configured_search_tool
