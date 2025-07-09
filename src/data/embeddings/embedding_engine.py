from typing import List
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv

# Load environment variables (if needed for other purposes)
load_dotenv()


class EmbeddingEngine:
    """
    A class that wraps the functionality for generating embeddings using Sentence-Transformers,
    with the ability to save and load its state.
    """

    def __init__(
        self,
        model_name: str = "all-MiniLM-L6-v2",
        save_path: str = "embedding_state.json",
    ):
        """
        Initialize the EmbeddingEngine.

        Args:
            model_name: The name of the Sentence-Transformers model to use.
            save_path: The path to the file where the embedding state will be saved/loaded.
        """
        # Initialize the Sentence-Transformer model
        self.model = SentenceTransformer(model_name)
        self.model_name = model_name
        self.corpus = []
        self.corpus_embeddings = None
        self.save_path = save_path

    def get_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for a list of texts.

        Args:
            texts: A list of text strings.

        Returns:
            A list of embeddings (list of floats) corresponding to each text.
        """
        embeddings = []
        for text in texts:
            embedding = self._generate_embedding(text)
            if embedding is not None:
                embeddings.append(embedding)
            else:
                print(
                    f"Warning: Embedding generation failed for text: '{text}'. Skipping."
                )
        return embeddings

    def get_query_embedding(self, query: str) -> List[float]:
        """
        Generate an embedding for a query string.

        Args:
            query: A query in string format.

        Returns:
            The embedding vector of the query.
        """
        return self._generate_embedding(query)

    def _generate_embedding(self, text: str) -> List[float]:
        """
        Generate an embedding using Sentence-Transformers for a given text.

        Args:
            text: A single text string to embed.

        Returns:
            A list of floats representing the text's embedding, or None if an error occurs.
        """
        try:
            # Generate embedding using Sentence-Transformers
            embedding = self.model.encode(text)
            # Convert the embedding from a NumPy array to a list of floats
            return embedding.tolist()
        except Exception as e:
            print(f"Error generating embedding for text: '{text}'. Error: {e}")
            return []
