from pymilvus import (
    connections,
    Collection,
    CollectionSchema,
    FieldSchema,
    DataType,
    utility,
)
from pymilvus import AnnSearchRequest, WeightedRanker
from typing import List, Dict, Any, Optional
import traceback
import os


class MilvusClient:
    def __init__(self, collection_name: str = "summerschool_workshop"):
        self.collection_name = collection_name
        self._connect()
        self._ensure_collection_exists()
        self.collection = Collection(self.collection_name)

    def _connect(self):
        try:
            connections.connect(
                alias="default",
                uri=os.getenv("MILVUS_URI"),
                token=f"{os.getenv('MILVUS_TOKEN')}",
            )
            # Verify connection
            if not connections.has_connection(alias="default"):
                raise Exception("Failed to establish connection to Milvus.")
        except Exception as e:
            print(f"Error connecting to Milvus: {e}")
            raise e

    def _ensure_connection(self):
        """Ensure the connection to Milvus is active."""
        if not connections.has_connection(alias="default"):
            print("Connection to Milvus is not active. Reconnecting...")
            self._connect()

    def _ensure_collection_exists(self):
        if not utility.has_collection(self.collection_name):
            print(f"Collection '{self.collection_name}' does not exist. Creating it...")
            schema = CollectionSchema(
                fields=[
                    FieldSchema(
                        name="ID", dtype=DataType.INT64, is_primary=True, auto_id=True
                    ),
                    FieldSchema(
                        name="Question", dtype=DataType.VARCHAR, max_length=65535
                    ),
                    FieldSchema(
                        name="Answer", dtype=DataType.VARCHAR, max_length=65535
                    ),
                    FieldSchema(
                        name="Question_dense_embedding",
                        dtype=DataType.FLOAT_VECTOR,
                        dim=384,
                    ),
                    FieldSchema(
                        name="Question_sparse_embedding",
                        dtype=DataType.SPARSE_FLOAT_VECTOR,
                    ),
                    FieldSchema(
                        name="Answer_dense_embedding",
                        dtype=DataType.FLOAT_VECTOR,
                        dim=384,
                    ),
                    FieldSchema(
                        name="Answer_sparse_embedding",
                        dtype=DataType.SPARSE_FLOAT_VECTOR,
                    ),
                ],
                description="FAQ collection schema",
            )
            Collection(name=self.collection_name, schema=schema)

    def index_data(
        self,
        Questions: List[str],
        Answers: List[str],
        Question_embeddings: List[List[float]],
        Answer_embeddings: List[List[float]],
        sparse_Question_embeddings: Optional[List[List[float]]] = None,
        sparse_Answer_embeddings: Optional[List[List[float]]] = None,
    ):
        """
        Index Questions, Answers, and their embeddings (both dense and sparse) into the Milvus collection.

        Args:
            Questions: List of Question strings to be indexed.
            Answers: List of Answer strings corresponding to the Questions.
            Question_embeddings: List of dense embeddings for the Questions.
            Answer_embeddings: List of dense embeddings for the Answers.
            sparse_Question_embeddings: Optional list of sparse embeddings for Questions.
            sparse_Answer_embeddings: Optional list of sparse embeddings for Answers.
        """
        # Ensure connection before proceeding
        self._ensure_connection()

        try:
            # Prepare the data to be inserted into Milvus
            entities = [
                {"name": "Question", "values": Questions, "type": DataType.VARCHAR},
                {"name": "Answer", "values": Answers, "type": DataType.VARCHAR},
                {"name": "Question_dense_embedding", "values": Question_embeddings, "type": DataType.FLOAT_VECTOR},
                {"name": "Answer_dense_embedding", "values": Answer_embeddings, "type": DataType.FLOAT_VECTOR}
            ]
            
            # Add sparse embeddings if provided
            if sparse_Question_embeddings:
                entities.append(
                    {"name": "Question_sparse_embedding", "values": sparse_Question_embeddings, "type": DataType.SPARSE_FLOAT_VECTOR}
                )
            if sparse_Answer_embeddings:
                entities.append(
                    {"name": "Answer_sparse_embedding", "values": sparse_Answer_embeddings, "type": DataType.SPARSE_FLOAT_VECTOR}
                )

            # Insert data into Milvus collection
            print(f"Inserting {len(Questions)} records into Milvus...")
            insert_result = self.collection.insert(entities)

            # Check if the data was successfully inserted
            if insert_result.insert_count == len(Questions):
                print(f"Successfully indexed {insert_result.insert_count} records.")
            else:
                print(f"Failed to insert all records. Only {insert_result.insert_count} were indexed.")
            
            # Optionally, create an index after inserting data
            self.create_index()

        except Exception as e:
            print(f"Error indexing data: {e}")
            traceback.print_exc()

    def create_index(self):
        """Create an index on the collection's vector fields for fast similarity search."""
        try:
            print("Creating index for Question dense embedding...")
            self.collection.create_index(
                field_name="Question_dense_embedding", 
                index_params={"metric_type": "L2", "index_type": "IVF_FLAT", "params": {"nlist": 128}}
            )

            print("Creating index for Answer dense embedding...")
            self.collection.create_index(
                field_name="Answer_dense_embedding", 
                index_params={"metric_type": "L2", "index_type": "IVF_FLAT", "params": {"nlist": 128}}
            )
            print("Index creation successful.")
        except Exception as e:
            print(f"Error creating index: {e}")
            traceback.print_exc()

   


    def hybrid_search(
        self,
        query_text: str,
        query_dense_embedding: List[float],
        limit: int = 5,
        search_answers: bool = False,
        ranker_weights: Optional[List[float]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Perform native hybrid search using Milvus's multi-vector search capabilities.

        This method combines dense vector search (semantic) and sparse vector search (BM25)
        using Milvus's built-in hybrid search functionality with reranking.

        Args:
            query_text: The text query for BM25 search
            query_dense_embedding: The dense embedding vector for semantic search
            limit: Maximum number of results to return
            search_answers: If True, search in Answer embeddings instead of Questions
            ranker_weights: Optional list of weights for the WeightedRanker (default is [0.7, 0.3])

        Returns:
            List of dictionaries containing search results with combined scores
        """
        # Ensure connection before proceeding
        self._ensure_connection()

        try:
            # Load collection into memory
            self.collection.load()
            print("Collection loaded successfully")
        except Exception as e:
            print(f"Error loading collection: {str(e)}")
            return []

        # Define search fields based on whether we're searching Answers or Questions
        dense_field = (
            "Answer_dense_embedding" if search_answers else "Question_dense_embedding"
        )
        sparse_field = (
            "Answer_sparse_embedding" if search_answers else "Question_sparse_embedding"
        )

        # Parameters for dense vector search
        dense_search_params = {"metric_type": "L2", "params": {"nprobe": 10}}

        # Parameters for sparse vector search (BM25)
        sparse_search_params = {"metric_type": "BM25", "params": {}}

        try:
            print("Setting up hybrid search following pymilvus API...")

            # For dense vector search (semantic similarity)
            search_param_1 = {
                "data": [query_dense_embedding],  # List containing the embedding vector
                "anns_field": dense_field,  # Use the correct field based on search_answers
                "param": dense_search_params,
                "limit": limit * 2,  # Get more results for reranking
            }
            # For sparse vector search (BM25 keyword matching)
            search_param_2 = {
                "data": [query_text],  # List containing the query text
                "anns_field": sparse_field,  # Use the correct field based on search_answers
                "param": sparse_search_params,
                "limit": limit * 2,  # Get more results for reranking
            }
            # Then you can use these with AnnSearchRequest
            request_1 = AnnSearchRequest(**search_param_1)
            request_2 = AnnSearchRequest(**search_param_2)
            print(f"Search requests prepared: {len([request_1, request_2])} requests")
            # Choose appropriate ranker based on documentation
            if ranker_weights:
                weight_ranker = WeightedRanker(*ranker_weights)
                print(f"Using custom weights for ranker: {ranker_weights}")
            else:
                # Default weights: 70% for dense vectors, 30% for sparse vectors
                weight_ranker = WeightedRanker(0.7, 0.3)
                print("Using default weights for ranker: [0.7, 0.3]")

            # Execute hybrid search with reranking - follow pymilvus API
            print("Executing hybrid search...")
            search_results = self.collection.hybrid_search(
                reqs=[request_1, request_2],  # Method expects 'data' parameter
                rerank=weight_ranker,  # Use rerank parameter with the WeightedRanker
                limit=10,  # Overall limit for results
                output_fields=["Question", "Answer"],
            )
            # Format results
            output = []
            for hits in search_results:  # type: ignore
                for hit in hits:
                    output.append(
                        {
                            "Question": hit.entity.get("Question"),
                            "Answer": hit.entity.get("Answer"),
                            "score": hit.score,
                        }
                    )
            print(f"Formatted {len(output)} results")
            return output
        except Exception as e2:
            print(f"Fallback search also failed: {str(e2)}")
            traceback.print_exc()

            # Final fallback to simple vector search
            try:
                print("Falling back to simple vector search")
                search_results = self.collection.search(
                    data=[query_dense_embedding],
                    anns_field=dense_field,
                    param=dense_search_params,
                    limit=limit,
                    output_fields=["Question", "Answer"],
                )
                output = []
                for hits in search_results:  # type: ignore
                    for hit in hits:
                        output.append(
                            {
                                "Question": hit.entity.get("Question"),
                                "Answer": hit.entity.get("Answer"),
                                "score": hit.score,
                            }
                        )
                return output
            except Exception as e3:
                print(f"All search methods failed: {str(e3)}")
                traceback.print_exc()
                return []
    
    
