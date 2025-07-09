import csv
import PyPDF2
import docx
from typing import List, Dict, Any, Union
from pydantic import BaseModel, Field
import os


class FileContentOutput(BaseModel):
    # Output model for file content.
    file_path: str = Field(..., description="The path of the read file.")
    content: Union[str, List[Dict[str, Any]]] = Field(
        ..., description="The content of the file."
    )
    success: bool = Field(True, description="Whether the file was read successfully.")
    error_message: str = Field("", description="Error message if reading failed.")


def read_file_tool(file_path: str) -> FileContentOutput:
    # Reads the content of a specified file (CSV, PDF, or DOCX).
    #
    # For CSV files, it returns a list of dictionaries.
    # For PDF and DOCX files, it extracts and returns the text content.

    file_path = file_path

    if not os.path.exists(file_path):
        return FileContentOutput(
            file_path=file_path,
            content="",
            success=False,
            error_message="File not found.",
        )

    _, file_extension = os.path.splitext(file_path)

    try:
        content: Union[str, List[Dict[str, Any]]]
        if file_extension.lower() == ".csv":
            with open(file_path, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                content = [row for row in reader]

        elif file_extension.lower() == ".pdf":
            text_content = []
            with open(file_path, "rb") as f:
                reader = PyPDF2.PdfReader(f)
                for page in reader.pages:
                    text_content.append(page.extract_text())
            content = "\n".join(text_content)

        elif file_extension.lower() == ".docx":
            doc = docx.Document(file_path)
            content = "\n".join([paragraph.text for paragraph in doc.paragraphs])

        else:
            return FileContentOutput(
                file_path=file_path,
                content="",
                success=False,
                error_message=f"Unsupported file type: {file_extension}",
            )

        return FileContentOutput(
            file_path=file_path, content=content, success=True, error_message=""
        )

    except Exception as e:
        return FileContentOutput(
            file_path=file_path, content="", success=False, error_message=str(e)
        )


def create_read_file_tool(file_path: str):
    """
    Create a read file tool function with a pre-configured file path.

    Args:
        file_path: Path to the file to be read

    Returns:
        A function that reads the specified file
    """

    def configured_read_file_tool() -> FileContentOutput:
        return read_file_tool(file_path)

    return configured_read_file_tool
