from utils.basetools.document_chunking_tool import document_chunking_tool, DocumentChunkingInput
from utils.basetools.search_relevant_document_tool import search_relevant_document, SearchRelevantDocumentInput

def run_document_workflow_test():
    import os
    test_document_path = os.path.join(os.path.dirname(__file__), "../data/mock_data/test_document.txt")
    collection_name = "test_document_collection"

    print(f"--- Starting Document Workflow Test ---")

    # Test Document Chunking Tool
    print(f"\n--- Testing document_chunking_tool ---")
    chunking_input = DocumentChunkingInput(
        model_name="gemini-2.0-flash",
        overlap=0,
        document_path=test_document_path,
        collection_name=collection_name,
        language="vi", #
        max_tokens=50,
        min_similarity=0.5
    )
    chunking_output = document_chunking_tool(chunking_input)
    print(f"Chunking Result: {chunking_output.message}")
    # print(f"Number of chunks indexed: {chunking_output.num_chunks}")

    if not chunking_output.success:
        print("Document chunking failed. Aborting test.")
        return

    # Test Search Relevant Document Tool
    print(f"\n--- Testing search_relevant_document ---")
    search_query = "được tính khấu trừ về thuế không?"
    search_input = SearchRelevantDocumentInput(
        user_query=search_query,
        k=2,
        threshold=0.0, # Set a low threshold for testing to ensure some results
        collection_name=collection_name
    )
    search_output = search_relevant_document(search_input)
    print(f"Search Query: '{search_query}'")
    print(f"Retrieved Documents ({len(search_output.documents)}):")
    for i, doc in enumerate(search_output.documents):
        print(f"  Document {i+1}: {doc}")

    print(f"\n--- Document Workflow Test Complete ---")

if __name__ == "__main__":
    run_document_workflow_test()
