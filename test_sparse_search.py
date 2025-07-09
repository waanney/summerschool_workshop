from pymilvus import Collection
from data.milvus.milvus_client import MilvusClient

def test_full_text_search():
    """Test BM25 full text search functionality"""
    client = MilvusClient()
    client._connect()
    
    collection = Collection("summerschool_workshop")
    collection.load()
    
    # Test search on Question field using BM25 sparse vectors
    search_params = {
        'params': {'drop_ratio_search': 0.2},
    }
    
    # Search for HR related questions
    results = collection.search(
        data=["nghỉ phép"],  # Vietnamese text query
        anns_field="Question_sparse_embedding",  # Use sparse field for BM25 search
        param=search_params,
        limit=5,
        output_fields=["Question", "Answer"]  # Don't include sparse field in output
    )
    
    print("=== BM25 FULL TEXT SEARCH RESULTS ===")
    for i, result in enumerate(results[0]):
        print(f"Result {i+1}:")
        print(f"  Score: {result.score}")
        print(f"  Question: {result.entity.get('Question')}")
        print(f"  Answer: {result.entity.get('Answer')}")
        print()

if __name__ == "__main__":
    test_full_text_search()
