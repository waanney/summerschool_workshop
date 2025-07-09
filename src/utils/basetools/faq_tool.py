from data.embeddings.embedding_engine import EmbeddingEngine
from data.milvus.milvus_client import MilvusClient
from typing import List
from pydantic import BaseModel, Field
from typing import Dict, Any

embedding_engine = EmbeddingEngine()


class SearchInput(BaseModel):
    query: str = Field(..., description="Search query")
    limit: int = Field(3, description="Number of top results to return")
    search_answers: bool = Field(
        False, description="Whether to search in answer embeddings"
    )


class SearchOutput(BaseModel):
    results: List[Dict[str, Any]] = Field(
        ..., description="Search results containing questions and answers"
    )


def faq_tool(
    input: SearchInput, collection_name: str = "summerschool_workshop"
) -> SearchOutput:
    client = MilvusClient(collection_name=collection_name)

    query_embedding = embedding_engine.get_query_embedding(input.query)

    results = client.hybrid_search(
        query_text=input.query,
        query_dense_embedding=query_embedding,
        limit=input.limit,
        search_answers=input.search_answers,
    )
    return SearchOutput(results=results)


def create_faq_tool(collection_name: str = "summerschool_workshop"):
    """
    Create a FAQ tool function with a pre-configured collection name.

    Args:
        collection_name: Name of the Milvus collection to use for searches

    Returns:
        A function that performs FAQ searches using the specified collection
    """

    def configured_faq_tool(input: SearchInput) -> SearchOutput:
        # Collection name is fixed and cannot be changed by the agent
        return faq_tool(input, collection_name=collection_name)

    return configured_faq_tool
