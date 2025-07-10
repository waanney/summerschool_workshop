import csv
import unicodedata
from rapidfuzz import fuzz
from typing import List, Dict, Any
from pydantic import BaseModel, Field


class SearchInput(BaseModel):
    query: str = Field(..., description="Search query")
    limit: int = Field(1, description="Number of top results to return")
    threshold: int = Field(60, description="Minimum fuzzy match score (0-100)")


class SearchOutput(BaseModel):
    results: List[Dict[str, Any]] = Field(
        ..., description="Search results containing questions, answers, and relevance scores"
    )


def normalize(text: str) -> str:
    """
    Normalize text by removing diacritics, converting to lowercase,
    and collapsing extra whitespace.
    """
    # Decompose unicode characters and remove diacritical marks
    text = unicodedata.normalize("NFD", text)
    text = "".join(ch for ch in text if unicodedata.category(ch) != "Mn")
    # Lowercase and collapse whitespace
    return " ".join(text.lower().split())


def search_in_file(
    input: SearchInput,
    file_path: str = "src/data/mock_data/admission_faq_large.csv"
) -> SearchOutput:
    """
    Search FAQ CSV file using both substring and fuzzy matching.

    - query: The search query
    - limit: Maximum number of results to return
    - threshold: Minimum fuzzy match score (0-100)

    Returns:
        SearchOutput with a list of dicts containing Question, Answer, and score.
    """
    # Normalize the query once
    q_norm = normalize(input.query)
    results: List[Dict[str, Any]] = []

    with open(file_path, "r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            question = row.get("Question", "")
            answer = row.get("Answer", "")

            # Normalize source text
            q_text = normalize(question)
            a_text = normalize(answer)

            # Compute fuzzy match scores
            score_q = fuzz.token_set_ratio(q_norm, q_text)
            score_a = fuzz.token_set_ratio(q_norm, a_text)
            best_score = max(score_q, score_a)

            # Check substring match OR fuzzy above threshold
            if q_norm in q_text or q_norm in a_text or best_score >= input.threshold:
                results.append({
                    "Question": question,
                    "Answer": answer,
                    "score": best_score,
                })

    # Sort by descending relevance
    results.sort(key=lambda x: x["score"], reverse=True)
    # Limit to top-N
    top_results = results[: input.limit]

    return SearchOutput(results=top_results)


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
