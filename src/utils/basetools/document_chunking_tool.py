"""
Document chunking and indexing module.

This module provides functionality for chunking documents into semantically coherent pieces
and indexing them into Milvus vector database. It supports multiple file formats including
TXT, PDF, and DOCX files with configurable chunking parameters.
"""

import csv
import os
import tempfile
import traceback
from pathlib import Path
from typing import List

from pydantic import BaseModel, Field
from enum import Enum

from data.milvus.indexing import MilvusIndexer, logger
from utils.basetools.semantic_splitter import (
    SemanticSplitter,
    load_txt,
    load_pdf,
    load_docx,
    Language,
    FileType,
)


class DocumentStatus(str, Enum):
    """Enum for document processing status."""
    SUCCESS = "success"
    FAILED = "failed"
    NOT_FOUND = "not_found"
    EMPTY = "empty"
    UNSUPPORTED_FORMAT = "unsupported_format"


class DocumentChunkingInput(BaseModel):
    """Input model for document chunking operations."""
    
    document_path: str = Field(
        ..., description="The absolute path to the document to be chunked."
    )
    collection_name: str = Field(
        ..., description="The name of the Milvus collection to store the chunks."
    )
    model_name: str = Field(
        "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
        description="The name of the sentence transformer model to use for semantic splitting.",
    )
    language: Language = Field(
        Language.MULTILINGUAL, description="The language of the document."
    )
    max_tokens: int = Field(200, description="The maximum number of tokens per chunk.")
    min_similarity: float = Field(
        0.6,
        description="The minimum similarity score for merging sentences into a chunk.",
    )
    overlap: int = Field(
        0, description="The number of overlapping sentences between chunks."
    )


class DocumentChunkingOutput(BaseModel):
    """Output model for document chunking operations."""
    
    success: bool = Field(
        ...,
        description="Indicates whether the document chunking and indexing was successful.",
    )
    message: str = Field(
        ..., description="A message describing the outcome of the operation."
    )
    num_chunks: int = Field(
        0, description="The number of chunks generated and indexed."
    )
    status: DocumentStatus = Field(
        DocumentStatus.FAILED, description="The status of the document processing."
    )


def document_chunking_tool(input: DocumentChunkingInput) -> DocumentChunkingOutput:
    """
    Chunks a document, saves it to a temporary CSV, and uses the MilvusIndexer
    class to index the data into Milvus.
    
    This function processes documents by:
    1. Loading the document content based on file type
    2. Splitting the content into semantically coherent chunks
    3. Creating a temporary CSV file with the chunks
    4. Indexing the chunks into Milvus using the MilvusIndexer
    5. Cleaning up temporary files
    
    Args:
        input: DocumentChunkingInput object containing all necessary parameters
        
    Returns:
        DocumentChunkingOutput: Object containing the operation result and metadata
        
    Raises:
        FileNotFoundError: If the document file doesn't exist
        ValueError: If the document is empty or unsupported format
        Exception: For any other processing errors
    """
    try:
        doc_path: Path = Path(input.document_path)
        if not doc_path.exists():
            return DocumentChunkingOutput(
                success=False,
                message=f"Document not found at {input.document_path}",
                num_chunks=0,
                status=DocumentStatus.NOT_FOUND,
            )

        # 1. Load document content
        content: str = _load_document_content(doc_path)
        if content is None:
            return DocumentChunkingOutput(
                success=False, 
                message="Unsupported file type", 
                num_chunks=0,
                status=DocumentStatus.UNSUPPORTED_FORMAT,
            )
        
        if not content:
            return DocumentChunkingOutput(
                success=False, 
                message="Document is empty.", 
                num_chunks=0,
                status=DocumentStatus.EMPTY,
            )

        # 2. Split document into chunks
        splitter: SemanticSplitter = SemanticSplitter(
            model_name=input.model_name,
            language=input.language,
            max_tokens=input.max_tokens,
            min_similarity=input.min_similarity,
            overlap=input.overlap,
        )
        chunks: List[str] = splitter.split(content)
        if not chunks:
            return DocumentChunkingOutput(
                success=False, 
                message="No chunks generated.", 
                num_chunks=0,
                status=DocumentStatus.FAILED,
            )

        # 3. Create a temporary CSV file from the chunks
        temp_csv_path: str = _create_temp_csv(chunks)
        logger.info(
            f"Created temporary CSV file with {len(chunks)} chunks at: {temp_csv_path}"
        )

        try:
            # 4. Instantiate and run the MilvusIndexer with the temp file
            indexer: MilvusIndexer = MilvusIndexer(
                collection_name=input.collection_name, 
                faq_file=temp_csv_path
            )
            indexer.run()

            message: str = (
                f"Successfully indexed {len(chunks)} chunks using MilvusIndexer. "
                f"NOTE: Embeddings were generated with the indexer's default model ('all-MiniLM-L6-v2')."
            )

            return DocumentChunkingOutput(
                success=True, 
                message=message, 
                num_chunks=len(chunks),
                status=DocumentStatus.SUCCESS,
            )

        finally:
            # 5. Clean up the temporary file
            os.remove(temp_csv_path)
            logger.info(f"Removed temporary CSV file: {temp_csv_path}")

    except Exception as e:
        traceback.print_exc()
        return DocumentChunkingOutput(
            success=False, 
            message=f"An error occurred: {str(e)}", 
            num_chunks=0,
            status=DocumentStatus.FAILED,
        )


def _load_document_content(doc_path: Path) -> str | None:
    """
    Load document content based on file extension.
    
    Args:
        doc_path: Path to the document file
        
    Returns:
        str | None: Document content or None if unsupported format
        
    Raises:
        FileNotFoundError: If the file doesn't exist
        UnicodeDecodeError: If text file encoding is not UTF-8
        PyPDF2.PdfReadError: If PDF is corrupted
        docx2txt.Docx2txtError: If DOCX is corrupted
    """
    file_extension: str = doc_path.suffix.lower()
    
    if file_extension == FileType.TXT:
        return load_txt(doc_path)
    elif file_extension == FileType.PDF:
        return load_pdf(doc_path)
    elif file_extension == FileType.DOCX:
        return load_docx(doc_path)
    else:
        return None


def _create_temp_csv(chunks: List[str]) -> str:
    """
    Create a temporary CSV file with document chunks.
    
    Args:
        chunks: List of text chunks to write to CSV
        
    Returns:
        str: Path to the created temporary CSV file
        
    Raises:
        IOError: If unable to create or write to temporary file
    """
    with tempfile.NamedTemporaryFile(
        mode="w", delete=False, suffix=".csv", newline="", encoding="utf-8"
    ) as temp_f:
        temp_csv_path: str = temp_f.name
        # MilvusIndexer expects a header. We will use 'text' as the column name.
        writer: csv.writer = csv.writer(temp_f)
        writer.writerow(["text"])  # Write header
        for chunk in chunks:
            writer.writerow([chunk])  # Write each chunk as a row
    
    return temp_csv_path
