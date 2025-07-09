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
import pandas as pd

# Setup logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MilvusIndexer:
    def __init__(
        self,
        collection_name="summerschool_workshop",
        faq_file="src/data/mock_data/admission_faq_large.csv",
    ):
        self.collection_name = collection_name
        self.faq_file = faq_file
        self.file_type = "csv" if faq_file.endswith(".csv") else "xlsx"
        self.milvus_client = MilvusClient()
        self.collection = None

    def connect(self):
        """Connect to the Milvus server."""
        self.milvus_client._connect()

    def create_collection(self, data_sample=None):
        """Create a Milvus collection with dynamic schema based on data columns."""
        # Get sample data to determine columns
        if data_sample is None:
            loader = (
                self.load_faq_data_from_csv
                if self.file_type == "csv"
                else self.load_faq_data_from_xlsx
            )
            sample_data = loader()
            if not sample_data:
                raise Exception("No data found to create schema")
            data_sample = sample_data[0]
        elif isinstance(data_sample, list) and len(data_sample) > 0:
            data_sample = data_sample[0]

        if not isinstance(data_sample, dict):
            raise Exception(f"Expected dictionary but got {type(data_sample)}")

        categories = list(data_sample.keys())

        # Drop existing collection
        if utility.has_collection(self.collection_name):
            utility.drop_collection(self.collection_name)
            logger.info(f"Dropped existing collection '{self.collection_name}'")

        # Create dynamic fields
        fields = [
            FieldSchema(name="ID", dtype=DataType.INT64, is_primary=True, auto_id=True)
        ]

        # Add text fields and dense embedding fields for each category
        # Also add sparse embedding fields for hybrid search
        for category in categories:
            fields.extend(
                [
                    FieldSchema(
                        name=category,
                        dtype=DataType.VARCHAR,
                        max_length=65535,
                        enable_analyzer=True,
                    ),
                    FieldSchema(
                        name=f"{category}_dense_embedding",
                        dtype=DataType.FLOAT_VECTOR,
                        dim=384,
                    ),
                    FieldSchema(
                        name=f"{category}_sparse_embedding",
                        dtype=DataType.SPARSE_FLOAT_VECTOR,
                    ),
                ]
            )

        # Skip BM25 functions for now to test basic functionality
        functions = []
        for category in categories:
            functions.append(
                Function(
                    name=f"{category}_bm25",
                    input_field_names=[category],
                    output_field_names=[f"{category}_sparse_embedding"],
                    function_type=FunctionType.BM25,
                )
            )

        schema = CollectionSchema(
            fields,
            description=f"Dynamic Milvus Collection for {categories}",
            enable_analyzers=True,
        )

        # Add BM25 functions to schema
        for func in functions:
            schema.add_function(func)

        self.collection = Collection(
            name=self.collection_name, schema=schema, using="default"
        )
        logger.info(
            f"Created collection '{self.collection_name}' with categories: {categories}"
        )

    def load_faq_data_from_csv(self):
        """Load FAQ data from the CSV file."""
        with open(self.faq_file, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            data = [
                {k: v for k, v in row.items() if v and str(v).strip()}
                for row in reader
                if any(v and str(v).strip() for v in row.values())
            ]
        logger.info(f"Loaded {len(data)} entries from {self.faq_file}.")
        return data

    def load_faq_data_from_xlsx(self):
        """Load FAQ data from the XLSX file with many sheets."""
        data = []
        for engine in ["openpyxl", "xlrd", "calamine"]:
            try:
                xls = pd.ExcelFile(self.faq_file, engine=engine)  # type: ignore
                for sheet_name in xls.sheet_names:
                    df = pd.read_excel(xls, sheet_name=sheet_name)
                    for _, row in df.iterrows():
                        row_data = {
                            k: v
                            for k, v in row.items()
                            if pd.notna(v) and str(v).strip()
                        }
                        if row_data:
                            data.append(row_data)
                logger.info(f"Loaded {len(data)} entries from {self.faq_file}.")
                return data
            except Exception:
                continue
        raise Exception(f"Could not open Excel file {self.faq_file}")

    def generate_embeddings(self, data):
        """Generate dense embeddings for all categories dynamically."""
        if not data:
            return [], []

        categories = list(data[0].keys())
        embedding_engine = EmbeddingEngine(model_name="all-MiniLM-L6-v2")

        category_texts = {}
        category_embeddings = {}

        # Generate embeddings for each category
        for category in categories:
            texts = [item.get(category, "") for item in data]
            embeddings = embedding_engine.get_embeddings(texts)
            category_texts[category] = texts
            category_embeddings[category] = embeddings

        return category_texts, category_embeddings

    def insert_data(self, data):
        """Insert data into the Milvus collection."""
        if self.collection is None:
            raise Exception(
                "Collection is not created. Call create_collection() first."
            )

        category_texts, category_embeddings = self.generate_embeddings(data)

        if isinstance(category_texts, dict):
            categories = list(category_texts.keys())
            print(categories)
            
            # Use simple array format - BM25 function will auto-generate sparse embeddings
            # Schema order: ID(auto), category1, category1_dense, category1_sparse(auto), category2, category2_dense, category2_sparse(auto)...
            # We provide: category1, category1_dense, category2, category2_dense (sparse auto-generated by BM25)
            entities = []
            
            for category in categories:
                entities.append(category_texts[category])  # Text field
                entities.append(category_embeddings[category])  # Dense embedding
                # Sparse embedding auto-generated by BM25 function - don't provide data

        else:
            # Fallback for old format
            entities = [category_texts, category_embeddings]

        logger.info(
            f"Inserting {len(data)} entries into collection '{self.collection_name}'"
        )
        logger.info(f"Categories: {categories}")
        logger.info(f"Entity arrays: {len(entities)}")
        for i, entity in enumerate(entities):
            logger.info(
                f"Entity {i}: {type(entity[0]) if entity else 'empty'} - length {len(entity)}"
            )

        insert_result = self.collection.insert(entities)
        self.collection.flush()

        logger.info(f"Successfully inserted {len(data)} records")
        return insert_result

    def create_index(self, categories=None):
        """Create indexes for dense and sparse embeddings dynamically."""
        if self.collection is None:
            raise Exception(
                "Collection is not created. Call create_collection() first."
            )

        # Get categories from collection schema if not provided
        if categories is None:
            field_names = [field.name for field in self.collection.schema.fields]
            categories = [
                name
                for name in field_names
                if not name.endswith("_embedding") and name != "ID"
            ]

        dense_index_params = {
            "index_type": "IVF_FLAT",
            "metric_type": "L2",
            "params": {"nlist": 128},
        }
        sparse_index_params = {
            "index_type": "SPARSE_INVERTED_INDEX",
            "metric_type": "BM25",
            "params": {
                "inverted_index_algo": "DAAT_MAXSCORE",
                "bm25_k1": 1.2,
                "bm25_b": 0.75,
            },
        }

        for category in categories:
            logger.info(f"Creating indexes for {category}...")
            self.collection.create_index(
                field_name=f"{category}_dense_embedding",
                index_params=dense_index_params,
            )
            self.collection.create_index(
                field_name=f"{category}_sparse_embedding",
                index_params=sparse_index_params,
            )

        self.collection.load()
        logger.info(
            f"All indexes created and collection loaded for categories: {categories}"
        )

    def run(self):
        """Run the indexing process."""
        self.connect()
        loader = (
            self.load_faq_data_from_csv
            if self.file_type == "csv"
            else self.load_faq_data_from_xlsx
        )
        faq_data = loader()
        self.create_collection(faq_data)
        self.create_index()
        self.insert_data(faq_data)
        logger.info("Data has been successfully inserted into Milvus.")


if __name__ == "__main__":
    indexer = MilvusIndexer(
        collection_name="summerschool_workshop",
        faq_file="src/data/mock_data/HR_FAQ_full.xlsx",
    )
    indexer.run()
