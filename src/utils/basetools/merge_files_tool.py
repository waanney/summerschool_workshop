"""
CSV file merging module.

This module provides functionality for merging multiple CSV files into a single
output file. It handles header management, row concatenation, and proper
encoding with comprehensive error handling.
"""

import csv
import os
from typing import List
from enum import Enum

from pydantic import BaseModel, Field


class MergeStatus(str, Enum):
    """Enum for merge operation status."""

    SUCCESS = "success"
    FAILED = "failed"
    FILE_NOT_FOUND = "file_not_found"
    INVALID_FORMAT = "invalid_format"


class MergeInput(BaseModel):
    """Input model for CSV file merging operations."""

    file_path1: str = Field(..., description="Path to the first CSV file")
    file_path2: str = Field(..., description="Path to the second CSV file")
    output_file_path: str = Field(..., description="Path to the output merged CSV file")
    skip_duplicates: bool = Field(False, description="Whether to skip duplicate rows")


class MergeOutput(BaseModel):
    """Output model for CSV file merging operations."""

    success: bool = Field(..., description="Indicates whether the merge was successful")
    output_path: str = Field(..., description="The path of the merged file")
    total_rows: int = Field(..., description="Total number of rows in the merged file")
    message: str = Field(
        "", description="Message indicating the result of the merge operation"
    )
    status: MergeStatus = Field(
        MergeStatus.FAILED, description="Status of the merge operation"
    )
    rows_from_file1: int = Field(0, description="Number of rows from the first file")
    rows_from_file2: int = Field(0, description="Number of rows from the second file")


def merge_files_tool(input_data: MergeInput) -> MergeOutput:
    """
    Merge two CSV files into a single CSV file.

    This function reads two CSV files and combines their rows into a single
    output file. The header from the first file is used, and the header from
    the second file is skipped. Duplicate handling can be configured.

    Args:
        input_data: MergeInput object containing file paths and merge options

    Returns:
        MergeOutput: Object containing merge results and metadata

    Raises:
        FileNotFoundError: If any of the input files don't exist
        csv.Error: If CSV format is invalid
        IOError: If unable to read or write files
        Exception: For any other merge errors
    """
    try:
        # Validate input files exist
        if not os.path.exists(input_data.file_path1):
            return MergeOutput(
                success=False,
                output_path="",
                total_rows=0,
                message=f"First file not found: {input_data.file_path1}",
                status=MergeStatus.FILE_NOT_FOUND,
            )

        if not os.path.exists(input_data.file_path2):
            return MergeOutput(
                success=False,
                output_path="",
                total_rows=0,
                message=f"Second file not found: {input_data.file_path2}",
                status=MergeStatus.FILE_NOT_FOUND,
            )

        # Read and merge files
        header: List[str]
        all_rows: List[List[str]]
        rows_from_file1: int
        rows_from_file2: int

        header, all_rows, rows_from_file1, rows_from_file2 = _merge_csv_files(
            input_data.file_path1, input_data.file_path2, input_data.skip_duplicates
        )

        # Write to the output file
        _write_merged_csv(input_data.output_file_path, header, all_rows)

        return MergeOutput(
            success=True,
            output_path=input_data.output_file_path,
            total_rows=len(all_rows),
            message=f"Successfully merged {input_data.file_path1} and {input_data.file_path2} into {input_data.output_file_path}",
            status=MergeStatus.SUCCESS,
            rows_from_file1=rows_from_file1,
            rows_from_file2=rows_from_file2,
        )

    except Exception as e:
        return MergeOutput(
            success=False,
            output_path="",
            total_rows=0,
            message=f"Failed to merge files: {str(e)}",
            status=MergeStatus.FAILED,
        )


def _merge_csv_files(
    file_path1: str, file_path2: str, skip_duplicates: bool
) -> tuple[List[str], List[List[str]], int, int]:
    """
    Merge two CSV files and return header, rows, and row counts.

    Args:
        file_path1: Path to the first CSV file
        file_path2: Path to the second CSV file
        skip_duplicates: Whether to skip duplicate rows

    Returns:
        tuple[List[str], List[List[str]], int, int]: Header, all rows, row counts from each file

    Raises:
        FileNotFoundError: If any file doesn't exist
        csv.Error: If CSV format is invalid
    """
    rows: List[List[str]] = []
    seen_rows: set[tuple[str, ...]] = set()

    # Read the first file
    with open(file_path1, "r", encoding="utf-8") as file1:
        reader1: csv.reader = csv.reader(file1)
        header: List[str] = next(reader1)  # Get header from the first file

        for row in reader1:
            if skip_duplicates:
                row_tuple: tuple[str, ...] = tuple(row)
                if row_tuple not in seen_rows:
                    rows.append(row)
                    seen_rows.add(row_tuple)
            else:
                rows.append(row)

    rows_from_file1: int = len(rows)

    # Read the second file
    with open(file_path2, "r", encoding="utf-8") as file2:
        reader2: csv.reader = csv.reader(file2)
        next(reader2)  # Skip header of the second file

        for row in reader2:
            if skip_duplicates:
                row_tuple = tuple(row)
                if row_tuple not in seen_rows:
                    rows.append(row)
                    seen_rows.add(row_tuple)
            else:
                rows.append(row)

    rows_from_file2: int = len(rows) - rows_from_file1

    return header, rows, rows_from_file1, rows_from_file2


def _write_merged_csv(
    output_path: str, header: List[str], rows: List[List[str]]
) -> None:
    """
    Write merged CSV data to output file.

    Args:
        output_path: Path to the output CSV file
        header: List of column headers
        rows: List of data rows

    Raises:
        IOError: If unable to write to the output file
        csv.Error: If CSV writing fails
    """
    with open(output_path, "w", newline="", encoding="utf-8") as outfile:
        writer: csv.writer = csv.writer(outfile)
        writer.writerow(header)
        writer.writerows(rows)
