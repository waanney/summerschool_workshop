from pymilvus import (
    Collection,
    FieldSchema,
    CollectionSchema,
    DataType,
    Function,
    FunctionType,
)
from ..embeddings.embedder import EmbeddingEngine
import json
from ..milvus.milvus_client import MilvusClient


class MilvusIndexer:
    def __init__(self, collection_name="vexere_database_4", faq_file="faq_data.json"):
        self.collection_name = collection_name
        self.faq_file = faq_file
        self.milvus_client = MilvusClient()
        self.collection = None

    def connect(self):
        """Connect to the Milvus server."""
        self.milvus_client._connect()

    def create_collection(self):
        """Create a Milvus collection with the specified schema."""
        fields = [
            FieldSchema(name="ID", dtype=DataType.INT64, is_primary=True, auto_id=True),
            FieldSchema(
                name="question",
                dtype=DataType.VARCHAR,
                max_length=65535,
                enable_analyzer=True,
            ),
            FieldSchema(
                name="answer",
                dtype=DataType.VARCHAR,
                max_length=65535,
                enable_analyzer=True,
            ),
            FieldSchema(
                name="question_dense_embedding", dtype=DataType.FLOAT_VECTOR, dim=1536
            ),
            FieldSchema(
                name="answer_dense_embedding", dtype=DataType.FLOAT_VECTOR, dim=1536
            ),
            FieldSchema(
                name="question_sparse_embedding", dtype=DataType.SPARSE_FLOAT_VECTOR
            ),
            FieldSchema(
                name="answer_sparse_embedding", dtype=DataType.SPARSE_FLOAT_VECTOR
            ),
        ]

        schema = CollectionSchema(
            fields,
            description="Milvus Collection with Question, Answer, Dense and Sparse Embeddings",
            enable_analyzers=True,
        )

        question_bm25 = Function(
            name="question_bm25",
            input_field_names=["question"],
            output_field_names=["question_sparse_embedding"],
            function_type=FunctionType.BM25,
        )
        answer_bm25 = Function(
            name="answer_bm25",
            input_field_names=["answer"],
            output_field_names=["answer_sparse_embedding"],
            function_type=FunctionType.BM25,
        )

        schema.add_function(question_bm25)
        schema.add_function(answer_bm25)

        self.collection = Collection(
            name=self.collection_name, schema=schema, using="default"
        )

    def load_faq_data(self):
        """Load FAQ data from the specified JSON file."""
        with open(self.faq_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data

    def generate_embeddings(self, data):
        """Generate dense and sparse embeddings for questions and answers."""
        questions = [item["question"] for item in data]
        answers = [item["answer"] for item in data]

        embedding_engine = EmbeddingEngine(model_name="text-embedding-3-small")

        question_dense_embeddings = embedding_engine.get_embeddings(questions)
        answer_dense_embeddings = embedding_engine.get_embeddings(answers)

        return questions, answers, question_dense_embeddings, answer_dense_embeddings

    def insert_data(self, data):
        """Insert data into the Milvus collection."""
        questions, answers, question_dense_embeddings, answer_dense_embeddings = (
            self.generate_embeddings(data)
        )

        entities = [
            questions,
            answers,
            question_dense_embeddings,
            answer_dense_embeddings,
        ]
        self.collection.insert(entities)

    def create_index(self):
        """Create indexes for dense and sparse embeddings."""
        dense_index_params = {
            "index_type": "IVF_FLAT",
            "metric_type": "L2",
            "params": {"nlist": 128},
        }
        self.collection.create_index(
            field_name="question_dense_embedding", index_params=dense_index_params
        )
        self.collection.create_index(
            field_name="answer_dense_embedding", index_params=dense_index_params
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
        self.collection.create_index(
            field_name="question_sparse_embedding", index_params=sparse_index_params
        )
        self.collection.create_index(
            field_name="answer_sparse_embedding", index_params=sparse_index_params
        )

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
