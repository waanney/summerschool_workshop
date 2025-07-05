from pymilvus import Collection
from data.embeddings.embedding_engine import EmbeddingEngine
from data.milvus.milvus_client import MilvusClient
from typing import List, Optional
from pydantic import BaseModel, Field
from typing import Dict, Any

milvus_client = MilvusClient()
milvus_client._connect()
collection = Collection("summerschool_workshop")
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

def faq_tool(input: SearchInput) -> SearchOutput:
    query_embedding = embedding_engine.get_query_embedding(input.query)

    results = milvus_client.hybrid_search(
        query_text=input.query,
        query_dense_embedding=query_embedding,
        limit=input.limit,
        search_answers=input.search_answers,
    )
    return SearchOutput(results=results)
