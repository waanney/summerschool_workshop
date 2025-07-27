"""
File reading and content extraction module.

This module provides functionality for reading and extracting content from various
file formats including CSV, PDF, and DOCX files. It supports structured data
extraction and text content retrieval with proper error handling.
"""

import csv
import os
from typing import List, Dict, Union
from enum import Enum

from pydantic import BaseModel, Field
import PyPDF2
import docx


class FileType(str, Enum):
    """Enum for supported file types."""
    CSV = "csv"
    PDF = "pdf"
    DOCX = "docx"
    TXT = "txt"


class FileStatus(str, Enum):
    """Enum for file reading status."""
    SUCCESS = "success"
    NOT_FOUND = "not_found"
    UNSUPPORTED_FORMAT = "unsupported_format"
    READ_ERROR = "read_error"


class FileContentOutput(BaseModel):
    """Output model for file content reading operations."""
    
    file_path: str = Field(..., description="The path of the read file")
    content: Union[str, List[Dict[str, str]]] = Field(
        ..., description="The content of the file"
    )
    success: bool = Field(True, description="Whether the file was read successfully")
    error_message: str = Field("", description="Error message if reading failed")
    file_type: FileType = Field(..., description="Type of the file that was read")
    status: FileStatus = Field(FileStatus.SUCCESS, description="Status of the file reading operation")


def read_file_tool(file_path: str) -> FileContentOutput:
    """
    Read the content of a specified file (CSV, PDF, DOCX, or TXT).
    
    This function supports multiple file formats:
    - CSV files: Returns a list of dictionaries with column headers as keys
    - PDF files: Extracts and returns text content from all pages
    - DOCX files: Extracts and returns text content from all paragraphs
    - TXT files: Returns the raw text content
    
    Args:
        file_path: Path to the file to be read
        
    Returns:
        FileContentOutput: Object containing the file content and operation status
        
    Raises:
        FileNotFoundError: If the file doesn't exist
        UnicodeDecodeError: If text file encoding is not UTF-8
        PyPDF2.PdfReadError: If PDF is corrupted
        docx.opc.exceptions.PackageNotFoundError: If DOCX is corrupted
        csv.Error: If CSV format is invalid
    """
    if not os.path.exists(file_path):
        return FileContentOutput(
            file_path=file_path,
            content="",
            success=False,
            error_message="File not found",
            file_type=FileType.TXT,  # Default fallback
            status=FileStatus.NOT_FOUND,
        )

    _, file_extension = os.path.splitext(file_path)
    file_type: FileType = _get_file_type(file_extension)

    try:
        content: Union[str, List[Dict[str, str]]] = _read_file_content(file_path, file_type)
        
        return FileContentOutput(
            file_path=file_path, 
            content=content, 
            success=True, 
            error_message="",
            file_type=file_type,
            status=FileStatus.SUCCESS,
        )

    except Exception as e:
        return FileContentOutput(
            file_path=file_path, 
            content="", 
            success=False, 
            error_message=str(e),
            file_type=file_type,
            status=FileStatus.READ_ERROR,
        )


def _get_file_type(file_extension: str) -> FileType:
    """
    Determine file type from file extension.
    
    Args:
        file_extension: File extension (e.g., '.csv', '.pdf')
        
    Returns:
        FileType: Enum value representing the file type
    """
    extension_lower: str = file_extension.lower()
    
    if extension_lower == ".csv":
        return FileType.CSV
    elif extension_lower == ".pdf":
        return FileType.PDF
    elif extension_lower == ".docx":
        return FileType.DOCX
    elif extension_lower == ".txt":
        return FileType.TXT
    else:
        return FileType.TXT  # Default fallback


def _read_file_content(file_path: str, file_type: FileType) -> Union[str, List[Dict[str, str]]]:
    """
    Read content from file based on its type.
    
    Args:
        file_path: Path to the file
        file_type: Type of the file to read
        
    Returns:
        Union[str, List[Dict[str, str]]]: File content in appropriate format
        
    Raises:
        FileNotFoundError: If the file doesn't exist
        UnicodeDecodeError: If text file encoding is not UTF-8
        PyPDF2.PdfReadError: If PDF is corrupted
        docx.opc.exceptions.PackageNotFoundError: If DOCX is corrupted
        csv.Error: If CSV format is invalid
    """
    if file_type == FileType.CSV:
        return _read_csv_file(file_path)
    elif file_type == FileType.PDF:
        return _read_pdf_file(file_path)
    elif file_type == FileType.DOCX:
        return _read_docx_file(file_path)
    elif file_type == FileType.TXT:
        return _read_txt_file(file_path)
    else:
        raise ValueError(f"Unsupported file type: {file_type}")


def _read_csv_file(file_path: str) -> List[Dict[str, str]]:
    """
    Read CSV file and return list of dictionaries.
    
    Args:
        file_path: Path to the CSV file
        
    Returns:
        List[Dict[str, str]]: List of dictionaries with column headers as keys
    """
    with open(file_path, "r", encoding="utf-8") as f:
        reader: csv.DictReader = csv.DictReader(f)
        return [row for row in reader]


def _read_pdf_file(file_path: str) -> str:
    """
    Read PDF file and extract text content.
    
    Args:
        file_path: Path to the PDF file
        
    Returns:
        str: Extracted text content from all pages
    """
    text_content: List[str] = []
    with open(file_path, "rb") as f:
        reader: PyPDF2.PdfReader = PyPDF2.PdfReader(f)
        for page in reader.pages:
            text_content.append(page.extract_text())
    return "\n".join(text_content)


def _read_docx_file(file_path: str) -> str:
    """
    Read DOCX file and extract text content.
    
    Args:
        file_path: Path to the DOCX file
        
    Returns:
        str: Extracted text content from all paragraphs
    """
    doc: docx.Document = docx.Document(file_path)
    return "\n".join([paragraph.text for paragraph in doc.paragraphs])


def _read_txt_file(file_path: str) -> str:
    """
    Read TXT file and return text content.
    
    Args:
        file_path: Path to the TXT file
        
    Returns:
        str: Raw text content
    """
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()


def create_read_file_tool(file_path: str) -> callable:
    """
    Create a read file tool function with a pre-configured file path.
    
    This factory function creates a configured file reading function that uses
    a specific file path. The file path is fixed and cannot be changed by the
    calling code.
    
    Args:
        file_path: Path to the file to be read
        
    Returns:
        callable: A function that reads the specified file
        
    Example:
        >>> read_my_file = create_read_file_tool("/path/to/my/file.csv")
        >>> result = read_my_file()
    """
    def configured_read_file_tool() -> FileContentOutput:
        """
        Configured file reading function with fixed file path.
        
        Returns:
            FileContentOutput: Object containing the file content and operation status
        """
        return read_file_tool(file_path)

    return configured_read_file_tool
