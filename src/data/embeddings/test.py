import unittest
from unittest.mock import patch
from ..embeddings.embedder import EmbeddingEngine  # Assuming your EmbeddingEngine class is saved in `embedding_engine.py`
from typing import List

class TestEmbeddingEngine(unittest.TestCase):
    
    @patch('google.genai.Client')  # Mock the `google.genai.Client` to avoid real API calls during testing
    def setUp(self, mock_client):
        """
        Set up the test case, creating an instance of the EmbeddingEngine
        and mocking the client.
        """
        # Mock response from the genai.Client
        mock_instance = mock_client.return_value
        mock_instance.models.embed_content.return_value = type('obj', (object,), {'data': [{'embedding': [0.1, 0.2, 0.3]}]})
        
        self.embedding_engine = EmbeddingEngine(model_name="embedding-001", save_path="embedding_state.json")
        
    def test_get_embeddings(self):
        """
        Test generating embeddings for a list of texts.
        """
        texts = ["Hello, how are you?", "This is a test sentence."]
        embeddings = self.embedding_engine.get_embeddings(texts)
        
        # Check if the embeddings list has the correct length (same as the input list)
        self.assertEqual(len(embeddings), len(texts))
        
        # Check if the embedding for each text is a list of floats
        for embedding in embeddings:
            self.assertIsInstance(embedding, list)
            self.assertTrue(all(isinstance(i, float) for i in embedding))
    
    def test_get_query_embedding(self):
        """
        Test generating embeddings for a single query.
        """
        query = "What is the capital of France?"
        embedding = self.embedding_engine.get_query_embedding(query)
        
        # Check if the returned embedding is a list of floats
        self.assertIsInstance(embedding, list)
        self.assertTrue(all(isinstance(i, float) for i in embedding))
    
    @patch('google.genai.Client')  # Mocking failed embedding generation scenario
    def test_failed_embedding_generation(self, mock_client):
        """
        Test the scenario where embedding generation fails and an empty list is returned.
        """
        # Modify the mock to simulate a failure
        mock_instance = mock_client.return_value
        mock_instance.models.embed_content.side_effect = Exception("Embedding service unavailable")
        
        texts = ["This text will fail."]
        embeddings = self.embedding_engine.get_embeddings(texts)
        
        # Ensure that no embeddings are returned
        self.assertEqual(embeddings, [])
        
    def test_handle_no_text(self):
        """
        Test when no text is provided, should return an empty list.
        """
        embeddings = self.embedding_engine.get_embeddings([])
        self.assertEqual(embeddings, [])
        
if __name__ == '__main__':
    unittest.main()
