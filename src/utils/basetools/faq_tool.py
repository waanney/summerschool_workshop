from pymilvus import Collection
from data.embeddings.embedding_engine import EmbeddingEngine
from data.milvus.milvus_client import MilvusClient
from typing import List, Optional
from pydantic import BaseModel, Field
from typing import Dict, Any


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


class FAQTool:
    """FAQ Search Tool using Milvus and Embedding Engine"""
    
    def __init__(self, collection_name: str = "summerschool_workshop"):
        """
        Initialize FAQ Tool
        
        Args:
            collection_name: Name of Milvus collection to use
        """
        self.collection_name = collection_name
        self.milvus_client = None
        self.collection = None
        self.embedding_engine = None
        self._initialized = False
    
    def initialize(self):
        """Initialize connections and engines"""
        if not self._initialized:
            self.milvus_client = MilvusClient()
            self.milvus_client._connect()
            self.collection = Collection(self.collection_name)
            self.embedding_engine = EmbeddingEngine()
            self._initialized = True
    
    def search(self, query: str, limit: int = 3, search_answers: bool = False) -> List[Dict[str, Any]]:
        """
        Search FAQ database
        
        Args:
            query: Search query string
            limit: Number of results to return
            search_answers: Whether to search in answer embeddings
            
        Returns:
            List of search results
        """
        if not self._initialized:
            self.initialize()
            
        query_embedding = self.embedding_engine.get_query_embedding(query)
        
        results = self.milvus_client.hybrid_search(
            query_text=query,
            query_dense_embedding=query_embedding,
            limit=limit,
            search_answers=search_answers,
        )
        
        return results
    
    def search_with_pydantic(self, input: SearchInput) -> SearchOutput:
        """
        Search using Pydantic models (for backward compatibility)
        
        Args:
            input: SearchInput model with query parameters
            
        Returns:
            SearchOutput model with results
        """
        results = self.search(
            query=input.query,
            limit=input.limit,
            search_answers=input.search_answers
        )
        return SearchOutput(results=results)
    
    def close(self):
        """Close connections"""
        if self.milvus_client:
            # Add any cleanup logic here if needed
            pass


# Global instance for backward compatibility
_faq_tool_instance = None

def get_faq_tool() -> FAQTool:
    """Get singleton FAQ tool instance"""
    global _faq_tool_instance
    if _faq_tool_instance is None:
        _faq_tool_instance = FAQTool()
        _faq_tool_instance.initialize()
    return _faq_tool_instance

def faq_tool(input: SearchInput) -> SearchOutput:
    """Legacy function for backward compatibility"""
    tool = get_faq_tool()
    return tool.search_with_pydantic(input)
