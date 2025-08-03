from pymilvus import (
    Collection,
    FieldSchema,
    CollectionSchema,
    DataType,
    Function,
    FunctionType,
    utility,
)
from data.embeddings.embedding_engine import EmbeddingEngine, EmbeddingModel
import csv
from data.milvus.milvus_client import MilvusClient
import logging
import pandas as pd
from typing import List, Dict, Tuple

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

    def connect(self) -> None:
        """Connect to the Milvus server."""
        self.milvus_client._connect()

    def create_collection(self, data_sample=None) -> None:
        """Create a Milvus collection with dynamic schema based on data columns."""
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

        for func in functions:
            schema.add_function(func)

        self.collection = Collection(
            name=self.collection_name, schema=schema, using="default"
        )
        logger.info(
            f"Created collection '{self.collection_name}' with categories: {categories}"
        )

    def load_faq_data_from_csv(self) -> List[Dict[str, str]]:
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

    def load_faq_data_from_xlsx(self) -> List[Dict[str, str]]:
        """Load FAQ data from the XLSX file with many sheets."""
        data = []
        for engine in ["openpyxl", "xlrd", "calamine"]:
            try:
                xls = pd.ExcelFile(self.faq_file, engine=engine)  # type: ignore
                for sheet_name in xls.sheet_names:
                    df = pd.read_excel(xls, sheet_name=sheet_name)
                    for _, row in df.iterrows():
                        row_data = {
                            str(k): str(v)
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

    def generate_embeddings(
        self, data
    ) -> Tuple[Dict[str, List[str]], Dict[str, List[List[float]]]]:
        """Generate dense embeddings for all categories dynamically."""
        if not data:
            return {}, {}

        categories = list(data[0].keys())
        embedding_engine = EmbeddingEngine(model_name=EmbeddingModel.MINI_LM_L6_V2)

        category_texts = {}
        category_embeddings = {}

        # Generate embeddings for each category
        for category in categories:
            texts = [item.get(category, "") for item in data]
            embeddings = embedding_engine.get_embeddings(texts)
            category_texts[category] = texts
            category_embeddings[category] = embeddings

        return category_texts, category_embeddings

    def insert_data(self, data) -> None:
        """Insert data into the Milvus collection."""
        if self.collection is None:
            raise Exception(
                "Collection is not created. Call create_collection() first."
            )
        category_texts, category_embeddings = self.generate_embeddings(data)

        if isinstance(category_texts, dict):
            categories = list(category_texts.keys())
            print(categories)

            # Create separate lists for each field
            entities = []
            for category in categories:
                # Add text data
                entities.append(category_texts[category])
                # Add dense embeddings
                entities.append(category_embeddings[category])
        else:
            categories = []
            entities = [category_texts, category_embeddings]

        logger.info(
            f"Inserting {len(data)} entries into collection '{self.collection_name}'"
        )
        logger.info(f"Categories: {str(categories)}")
        logger.info(f"Entity arrays: {len(entities)}")
        for i, entity in enumerate(entities):
            if isinstance(entity, (list, tuple)) and entity:
                entity_type = type(entity[0])
            else:
                entity_type = type(entity)
            logger.info(f"Entity {i}: {entity_type if entity else 'empty'}")

        insert_result = self.collection.insert(entities)
        self.collection.flush()
        logger.info(f"Successfully inserted {len(data)} records")
        logger.info(f"Insert result: {insert_result}")

    def create_index(self, categories=None) -> None:
        """Create indexes for dense and sparse embeddings dynamically."""
        if self.collection is None:
            raise Exception(
                "Collection is not created. Call create_collection() first."
            )

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

        self.collection.load(replica_number=1)
        logger.info(
            f"All indexes created and collection loaded for categories: {categories}"
        )

    def run(self) -> None:
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
