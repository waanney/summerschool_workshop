import csv
from typing import List
from pydantic import BaseModel, Field

class MergeInput(BaseModel):
    file_path1: str = Field(..., description="Path to the first CSV file")
    file_path2: str = Field(..., description="Path to the second CSV file")
    output_file_path: str = Field(..., description="Path to the output merged CSV file")

class MergeOutput(BaseModel):
    success: bool = Field(..., description="Indicates whether the merge was successful")
    output_path: str = Field(..., description="The path of the merged file")
    total_rows: int = Field(..., description="Total number of rows in the merged file")
    message: str = Field("", description="Message indicating the result of the merge operation")

def merge_files_tool(input_data: MergeInput) -> MergeOutput:
    """
    Merges two CSV files into a single CSV file.
    """
    try:
        rows = []
        # Read the first file
        with open(input_data.file_path1, 'r', encoding='utf-8') as file1:
            reader1 = csv.reader(file1)
            header = next(reader1)  # Get header from the first file
            rows.extend(list(reader1))

        # Read the second file
        with open(input_data.file_path2, 'r', encoding='utf-8') as file2:
            reader2 = csv.reader(file2)
            next(reader2)  # Skip header of the second file
            rows.extend(list(reader2))

        # Write to the output file
        with open(input_data.output_file_path, 'w', newline='', encoding='utf-8') as outfile:
            writer = csv.writer(outfile)
            writer.writerow(header)
            writer.writerows(rows)

        return MergeOutput(
            success=True,
            output_path=input_data.output_file_path,
            total_rows=len(rows),
            message=f"Successfully merged {input_data.file_path1} and {input_data.file_path2} into {input_data.output_file_path}"
        )
    except Exception as e:
        return MergeOutput(success=False, output_path="", total_rows=0, message=f"Failed to merge files: {str(e)}")
