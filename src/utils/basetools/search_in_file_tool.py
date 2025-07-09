import csv
from typing import List, Dict, Any
from pydantic import BaseModel, Field


class SearchInput(BaseModel):
    query: str = Field(..., description="Search query")
    limit: int = Field(1, description="Number of top results to return")


class SearchOutput(BaseModel):
    results: List[Dict[str, Any]] = Field(
        ..., description="Search results containing questions and answers"
    )


def search_in_file(
    input: SearchInput, file_path: str = "src/data/mock_data/admission_faq_large.csv"
) -> SearchOutput:
    results = []
    query_lower = input.query.lower()

    with open(file_path, "r", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        for row in reader:
            question = row.get("Question", "").lower()
            answer = row.get("Answer", "").lower()
            if query_lower in question or query_lower in answer:
                results.append(
                    {
                        "Question": row.get("Question", ""),
                        "Answer": row.get("Answer", ""),
                    }
                )
            if len(results) >= input.limit:
                break

    return SearchOutput(results=results)


def create_search_in_file_tool(
    file_path: str = "src/data/mock_data/admission_faq_large.csv",
):
    """
    Create a search tool function with a pre-configured file path.

    Args:
        file_path: Path to the CSV file to search in

    Returns:
        A function that performs searches in the specified CSV file
    """

    def configured_search_in_file_tool(input: SearchInput) -> SearchOutput:
        return search_in_file(input, file_path=file_path)

    return configured_search_in_file_tool
