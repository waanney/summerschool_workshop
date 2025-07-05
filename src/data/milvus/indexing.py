from pymilvus import (
    Collection,
    FieldSchema,
    CollectionSchema,
    DataType,
    Function,
    FunctionType,
    utility,
)
from data.embeddings.embedding_engine import EmbeddingEngine
import json
import csv
from data.milvus.milvus_client import MilvusClient
import logging

# Setup logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MilvusIndexer:
    def __init__(self, collection_name="summerschool_workshop", faq_file="admission_faq_large.csv"):
        self.collection_name = collection_name
        self.faq_file = faq_file
        self.milvus_client = MilvusClient()
        self.collection = None

    def connect(self):
        """Connect to the Milvus server."""
        self.milvus_client._connect()

    def create_collection(self):
        """Create a Milvus collection with the specified schema."""
        # Check if collection exists and drop it if schema doesn't match
        if utility.has_collection(self.collection_name):
            logger.info(f"Collection '{self.collection_name}' already exists. Dropping it to recreate with new schema.")
            try:
                # Force drop the collection to avoid schema conflicts
                utility.drop_collection(self.collection_name)
                logger.info(f"Successfully dropped existing collection '{self.collection_name}'")
            except Exception as e:
                logger.error(f"Error dropping collection: {e}")
                raise e
        
        try:
            fields = [
                FieldSchema(name="ID", dtype=DataType.INT64, is_primary=True, auto_id=True),
                FieldSchema(
                    name="Question",
                    dtype=DataType.VARCHAR,
                    max_length=65535,
                    enable_analyzer=True,
                ),
                FieldSchema(
                    name="Answer",
                    dtype=DataType.VARCHAR,
                    max_length=65535,
                    enable_analyzer=True,
                ),
                FieldSchema(
                    name="Question_dense_embedding", dtype=DataType.FLOAT_VECTOR, dim=384
                ),
                FieldSchema(
                    name="Answer_dense_embedding", dtype=DataType.FLOAT_VECTOR, dim=384
                ),
                FieldSchema(
                    name="Question_sparse_embedding", dtype=DataType.SPARSE_FLOAT_VECTOR
                ),
                FieldSchema(
                    name="Answer_sparse_embedding", dtype=DataType.SPARSE_FLOAT_VECTOR
                ),
            ]

            schema = CollectionSchema(
                fields,
                description="Milvus Collection with Question, Answer, Dense and Sparse Embeddings",
                enable_analyzers=True,
            )

            Question_bm25 = Function(
                name="Question_bm25",
                input_field_names=["Question"],
                output_field_names=["Question_sparse_embedding"],
                function_type=FunctionType.BM25,
            )
            Answer_bm25 = Function(
                name="Answer_bm25",
                input_field_names=["Answer"],
                output_field_names=["Answer_sparse_embedding"],
                function_type=FunctionType.BM25,
            )

            schema.add_function(Question_bm25)
            schema.add_function(Answer_bm25)

            self.collection = Collection(
                name=self.collection_name, schema=schema, using="default"
            )
            logger.info(f"Successfully created collection '{self.collection_name}' with new schema")
            
        except Exception as e:
            logger.error(f"Error creating collection: {e}")
            raise e

    def load_faq_data(self):
        """Load FAQ data from the specified CSV file."""
        with open(self.faq_file, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            data = [row for row in reader if row["Question"] and row["Answer"]]
        json_data = json.dumps(data, ensure_ascii=False)
        logger.info(f"Loaded {len(data)} FAQ entries from {self.faq_file}.")
        return json.loads(json_data)

    def generate_embeddings(self, data):
        """Generate dense and sparse embeddings for Questions and Answers."""
        Questions = [item["Question"] for item in data]
        Answers = [item["Answer"] for item in data]

        # Use a valid sentence-transformers model instead of OpenAI model
        embedding_engine = EmbeddingEngine(model_name="all-MiniLM-L6-v2")

        Question_dense_embeddings = embedding_engine.get_embeddings(Questions)
        Answer_dense_embeddings = embedding_engine.get_embeddings(Answers)

        return Questions, Answers, Question_dense_embeddings, Answer_dense_embeddings

    def insert_data(self, data):
        """Insert data into the Milvus collection."""
        try:
            Questions, Answers, Question_dense_embeddings, Answer_dense_embeddings = (
                self.generate_embeddings(data)
            )

            entities = [
                Questions,
                Answers,
                Question_dense_embeddings,
                Answer_dense_embeddings,
            ]
            
            logger.info(f"Inserting {len(Questions)} FAQ entries into collection '{self.collection_name}'")
            insert_result = self.collection.insert(entities)
            
            if hasattr(insert_result, 'insert_count'):
                logger.info(f"Successfully inserted {insert_result.insert_count} records")
            else:
                logger.info(f"Data insertion completed for {len(Questions)} records")
                
        except Exception as e:
            logger.error(f"Error inserting data: {e}")
            raise e

    def create_index(self):
        """Create indexes for dense and sparse embeddings."""
        try:
            dense_index_params = {
                "index_type": "IVF_FLAT",
                "metric_type": "L2",
                "params": {"nlist": 128},
            }
            
            logger.info("Creating index for Question dense embedding...")
            self.collection.create_index(
                field_name="Question_dense_embedding", index_params=dense_index_params
            )
            
            logger.info("Creating index for Answer dense embedding...")
            self.collection.create_index(
                field_name="Answer_dense_embedding", index_params=dense_index_params
            )

            sparse_index_params = {
                "index_type": "SPARSE_INVERTED_INDEX",
                "metric_type": "BM25",
                "params": {
                    "inverted_index_algo": "DAAT_MAXSCORE",
                    "bm25_k1": 1.2,
                    "bm25_b": 0.75,
                },
            }
            
            logger.info("Creating index for Question sparse embedding...")
            self.collection.create_index(
                field_name="Question_sparse_embedding", index_params=sparse_index_params
            )
            
            logger.info("Creating index for Answer sparse embedding...")
            self.collection.create_index(
                field_name="Answer_sparse_embedding", index_params=sparse_index_params
            )
            
            logger.info("All indexes created successfully")
            
        except Exception as e:
            logger.error(f"Error creating index: {e}")
            raise e

    def run(self):
        """Run the indexing process."""
        self.connect()
        self.create_collection()
        self.create_index()
        faq_data = self.load_faq_data()
        self.insert_data(faq_data)
        logger.info("Data has been successfully inserted into Milvus.")


if __name__ == "__main__":
    indexer = MilvusIndexer()
    indexer.run()
