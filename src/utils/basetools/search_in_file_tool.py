"""
File search and fuzzy matching module.

This module provides functionality for searching within CSV files using both
substring and fuzzy matching algorithms. It supports multilingual text normalization,
configurable similarity thresholds, and relevance scoring.
"""

import csv
import unicodedata
from typing import List, Dict, Callable
from enum import Enum

from rapidfuzz import fuzz
from pydantic import BaseModel, Field


class SearchMode(str, Enum):
    """Enum for search modes."""

    SUBSTRING = "substring"
    FUZZY = "fuzzy"
    HYBRID = "hybrid"


class SearchStatus(str, Enum):
    """Enum for search operation status."""

    SUCCESS = "success"
    FILE_NOT_FOUND = "file_not_found"
    NO_RESULTS = "no_results"
    ERROR = "error"


class SearchInput(BaseModel):
    """Input model for file search operations."""

    query: str = Field(..., description="Search query text")
    limit: int = Field(1, description="Number of top results to return")
    threshold: int = Field(60, description="Minimum fuzzy match score (0-100)")
    search_mode: SearchMode = Field(SearchMode.HYBRID, description="Search mode to use")


class SearchResult(BaseModel):
    """Model for individual search results."""

    question: str = Field(..., description="The question text")
    answer: str = Field(..., description="The answer text")
    score: float = Field(..., description="Relevance score (0-100)")
    match_type: str = Field(..., description="Type of match (substring/fuzzy)")


class SearchOutput(BaseModel):
    """Output model for file search operations."""

    results: List[SearchResult] = Field(
        ...,
        description="List of search results with questions, answers, and relevance scores",
    )
    total_found: int = Field(..., description="Total number of results found")
    query: str = Field(..., description="The original search query")
    status: SearchStatus = Field(
        SearchStatus.SUCCESS, description="Status of the search operation"
    )


def normalize(text: str) -> str:
    """
    Normalize text by removing diacritics, converting to lowercase,
    and collapsing extra whitespace.

    This function is particularly useful for multilingual text processing
    as it removes diacritical marks while preserving the base characters.

    Args:
        text: Input text to normalize

    Returns:
        str: Normalized text string

    Example:
        >>> normalize("Hà Nội")
        'ha noi'
        >>> normalize("São Paulo")
        'sao paulo'
    """
    # Decompose unicode characters and remove diacritical marks
    text = unicodedata.normalize("NFD", text)
    text = "".join(ch for ch in text if unicodedata.category(ch) != "Mn")
    # Lowercase and collapse whitespace
    return " ".join(text.lower().split())


def search_in_file(
    input: SearchInput, file_path: str = "workflow/_data/output.csv"
) -> SearchOutput:
    """
    Search FAQ CSV file using both substring and fuzzy matching.

    This function performs semantic search within a CSV file containing
    question-answer pairs. It supports multiple search modes and provides
    relevance scoring for results.

    Args:
        input: SearchInput object containing query and search parameters
        file_path: Path to the CSV file to search in

    Returns:
        SearchOutput: Object containing search results and metadata

    Raises:
        FileNotFoundError: If the CSV file doesn't exist
        csv.Error: If CSV format is invalid
        UnicodeDecodeError: If file encoding is not UTF-8
        Exception: For any other search errors
    """
    try:
        # Normalize the query once
        q_norm: str = normalize(input.query)
        results: List[SearchResult] = []

        with open(file_path, "r", encoding="utf-8", newline="") as f:
            reader: csv.DictReader = csv.DictReader(f)
            for row in reader:
                question: str = row.get("Question", "")
                answer: str = row.get("Answer", "")

                # Normalize source text
                q_text: str = normalize(question)
                a_text: str = normalize(answer)

                # Compute fuzzy match scores
                score_q: float = fuzz.token_set_ratio(q_norm, q_text)
                score_a: float = fuzz.token_set_ratio(q_norm, a_text)
                best_score: float = max(score_q, score_a)

                # Determine match type and check if result should be included
                match_type: str = _determine_match_type(
                    q_norm, q_text, a_text, best_score, input.threshold
                )

                if match_type != "none":
                    search_result: SearchResult = SearchResult(
                        question=question,
                        answer=answer,
                        score=best_score,
                        match_type=match_type,
                    )
                    results.append(search_result)

        # Sort by descending relevance
        results.sort(key=lambda x: x.score, reverse=True)
        # Limit to top-N
        top_results: List[SearchResult] = results[: input.limit]

        return SearchOutput(
            results=top_results,
            total_found=len(results),
            query=input.query,
            status=SearchStatus.SUCCESS if top_results else SearchStatus.NO_RESULTS,
        )

    except FileNotFoundError:
        return SearchOutput(
            results=[],
            total_found=0,
            query=input.query,
            status=SearchStatus.FILE_NOT_FOUND,
        )
    except Exception as e:
        return SearchOutput(
            results=[], total_found=0, query=input.query, status=SearchStatus.ERROR
        )


def _determine_match_type(
    query_norm: str,
    question_norm: str,
    answer_norm: str,
    best_score: float,
    threshold: int,
) -> str:
    """
    Determine the type of match based on search criteria.

    Args:
        query_norm: Normalized query text
        question_norm: Normalized question text
        answer_norm: Normalized answer text
        best_score: Best fuzzy match score
        threshold: Minimum threshold for fuzzy matching

    Returns:
        str: Match type ("substring", "fuzzy", or "none")
    """
    # Check substring match
    if query_norm in question_norm or query_norm in answer_norm:
        return "substring"
    # Check fuzzy match above threshold
    elif best_score >= threshold:
        return "fuzzy"
    else:
        return "none"


def create_search_in_file_tool(
    file_path: str = "workflow/_data/output.csv",
) -> Callable[[SearchInput], SearchOutput]:
    """
    Create a search tool function with a pre-configured file path.

    This factory function creates a configured search function that uses
    a specific CSV file path. The file path is fixed and cannot be changed
    by the calling code.

    Args:
        file_path: Path to the CSV file to search in

    Returns:
        Callable[[SearchInput], SearchOutput]: A function that performs searches in the specified CSV file

    Example:
        >>> search_tool = create_search_in_file_tool("/path/to/faq.csv")
        >>> result = search_tool(SearchInput(query="How to reset password?"))
    """

    def configured_search_in_file_tool(input: SearchInput) -> SearchOutput:
        """
        Configured search function with fixed file path.

        Args:
            input: SearchInput object containing query and search parameters

        Returns:
            SearchOutput: Object containing search results and metadata
        """
        return search_in_file(input, file_path=file_path)

    return configured_search_in_file_tool
