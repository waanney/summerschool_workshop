from pymilvus import Collection
from data.embeddings.embedding_engine import EmbeddingEngine
from data.milvus.milvus_client import MilvusClient
from typing import List, Optional
from pydantic import BaseModel, Field
from typing import Dict, Any

embedding_engine = EmbeddingEngine()

class SearchInput(BaseModel):
    query: str = Field(..., description="Search query")
    limit: int = Field(3, description="Number of top results to return")
    search_answers: bool = Field(
        False, description="Whether to search in answer embeddings"
    )
    collection_name: str = Field(
        "summerschool_workshop", description="Name of the Milvus collection to search in"
    )


class SearchOutput(BaseModel):
    results: List[Dict[str, Any]] = Field(
        ..., description="Search results containing questions and answers"
    )

def faq_tool(input: SearchInput) -> SearchOutput:
    client = MilvusClient(collection_name=input.collection_name)
    
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
        if input.collection_name == "summerschool_workshop":
            input.collection_name = collection_name
        
        return faq_tool(input)
    
    return configured_faq_tool
