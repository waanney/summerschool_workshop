import csv
from typing import List, Dict, Any

from data.milvus.indexing import MilvusIndexer, logger
from pydantic import BaseModel, Field
from pathlib import Path
import tempfile
from data.embeddings.embedding_engine import EmbeddingEngine
from data.milvus.milvus_client import MilvusClient
from utils.basetools.semantic_splitter import SemanticSplitter, load_txt, load_pdf, load_docx

import os
import traceback
from typing import List, Dict, Any

from pymilvus import (
    connections,
    utility,
    Collection,
    CollectionSchema,
    FieldSchema,
    DataType,
)


# Set environment variables for Milvus connection
# Ensure these are set in your environment before running the script
# os.environ["MILVUS_URI"] = "your-milvus-uri"
# os.environ["MILVUS_TOKEN"] = "your-milvus-token"



class DocumentChunkingInput(BaseModel):
    document_path: str = Field(..., description="The absolute path to the document to be chunked.")
    collection_name: str = Field(..., description="The name of the Milvus collection to store the chunks.")
    model_name: str = Field("bkai-foundation-models/vietnamese-bi-encoder", description="The name of the sentence transformer model to use for semantic splitting.")
    language: str = Field("vi", description="The language of the document ('en' or 'vi').")
    max_tokens: int = Field(200, description="The maximum number of tokens per chunk.")
    min_similarity: float = Field(0.6, description="The minimum similarity score for merging sentences into a chunk.")
    overlap: int = Field(0, description="The number of overlapping sentences between chunks.")

class DocumentChunkingOutput(BaseModel):
    success: bool = Field(..., description="Indicates whether the document chunking and indexing was successful.")
    message: str = Field(..., description="A message describing the outcome of the operation.")
    num_chunks: int = Field(0, description="The number of chunks generated and indexed.")


def document_chunking_tool(input: DocumentChunkingInput) -> DocumentChunkingOutput:
    """
    Chunks a document, saves it to a temporary CSV, and uses the unmodified
    MilvusIndexer class to index the data into Milvus.
    """
    try:
        doc_path = Path(input.document_path)
        if not doc_path.exists():
            return DocumentChunkingOutput(success=False, message=f"Document not found at {input.document_path}")

        # 1. Load document content
        if doc_path.suffix.lower() == ".txt":
            content = load_txt(doc_path)
        elif doc_path.suffix.lower() == ".pdf":
            content = load_pdf(doc_path)
        elif doc_path.suffix.lower() == ".docx":
            content = load_docx(doc_path)
        else:
            return DocumentChunkingOutput(success=False, message=f"Unsupported file type")

        if not content: return DocumentChunkingOutput(success=False, message="Document is empty.")

        # 2. Split document into chunks. The model_name from input is used here.
        splitter = SemanticSplitter(model_name=input.model_name, language=input.language, max_tokens=input.max_tokens,
                                    min_similarity=input.min_similarity, overlap=input.overlap)
        chunks = splitter.split(content)
        if not chunks: return DocumentChunkingOutput(success=False, message="No chunks generated.")

        # 3. Create a temporary CSV file from the chunks
        # The `with` statement ensures the file is deleted automatically after use
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv', newline='', encoding='utf-8') as temp_f:
            temp_csv_path = temp_f.name
            # MilvusIndexer expects a header. We will use 'text' as the column name.
            writer = csv.writer(temp_f)
            writer.writerow(['text'])  # Write header
            for chunk in chunks:
                writer.writerow([chunk])  # Write each chunk as a row

        logger.info(f"Created temporary CSV file with {len(chunks)} chunks at: {temp_csv_path}")

        try:
            # 4. Instantiate and run the unmodified MilvusIndexer with the temp file
            # NOTE: MilvusIndexer will now use its own hardcoded embedding model ('all-MiniLM-L6-v2')
            # and schema logic.
            indexer = MilvusIndexer(
                collection_name=input.collection_name,
                faq_file=temp_csv_path
            )
            indexer.run()

            message = (f"Successfully indexed {len(chunks)} chunks using MilvusIndexer. "
                       f"NOTE: Embeddings were generated with the indexer's default model ('all-MiniLM-L6-v2').")

            return DocumentChunkingOutput(success=True, message=message, num_chunks=len(chunks))

        finally:
            # 5. Clean up the temporary file
            os.remove(temp_csv_path)
            logger.info(f"Removed temporary CSV file: {temp_csv_path}")

    except Exception as e:
        traceback.print_exc()
        return DocumentChunkingOutput(success=False, message=f"An error occurred: {str(e)}")