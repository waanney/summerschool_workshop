from typing import List, Dict, Any

from pydantic import BaseModel, Field

from data.embeddings.embedding_engine import EmbeddingEngine
from data.milvus.milvus_client import MilvusClient

embedding_engine = EmbeddingEngine()

class SearchRelevantDocumentInput(BaseModel):
    user_query: str = Field(..., description="The user's query to search for relevant documents.")
    k: int = Field(3, description="The maximum number of documents to return.")
    threshold: float = Field(0.7, description="The minimum similarity score for a document to be considered relevant.")
    collection_name: str = Field("summerschool_workshop", description="The name of the Milvus collection to search in.")

class SearchRelevantDocumentOutput(BaseModel):
    documents: List[str] = Field(..., description="A list of relevant document chunks retrieved from the vector database.")
    
def search_relevant_document(input: SearchRelevantDocumentInput) -> SearchRelevantDocumentOutput:
    """
    To function as a core retrieval component in a Retrieval-Augmented Generation (RAG) system
    by fetching relevant document passages based on a user query.
    This tool retrieves raw, relevant text chunks from a knowledge base, whereas the FAQ tool
    matches a query to a pre-defined question and returns its corresponding pre-written answer.
    """
    client = MilvusClient(collection_name=input.collection_name)
    
    query_embedding = embedding_engine.get_query_embedding(input.user_query)
    
    search_results = client.hybrid_search(
        query_dense_embedding=query_embedding,
        limit=input.k,
        query_text=input.user_query
    )
    
    relevant_documents = []
    for result in search_results:
        if result.get('score', 0.0) >= input.threshold:
            relevant_documents.append(result.get('text', ''))
            
    return SearchRelevantDocumentOutput(documents=relevant_documents)
