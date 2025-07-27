"""
Web search and content extraction module.

This module provides functionality for performing web searches using DuckDuckGo
and extracting search results including titles and links. It supports configurable
result limits and proper error handling.
"""

import requests
from typing import List, Dict
from enum import Enum

from pydantic import BaseModel, Field
from bs4 import BeautifulSoup


class SearchEngine(str, Enum):
    """Enum for supported search engines."""
    DUCKDUCKGO = "duckduckgo"
    GOOGLE = "google"
    BING = "bing"


class SearchStatus(str, Enum):
    """Enum for search operation status."""
    SUCCESS = "success"
    NO_RESULTS = "no_results"
    REQUEST_FAILED = "request_failed"
    PARSE_ERROR = "parse_error"


class SearchInput(BaseModel):
    """Input model for web search operations."""
    
    query: str = Field(..., description="Search query text")
    max_results: int = Field(5, description="Maximum number of results to return")
    search_engine: SearchEngine = Field(SearchEngine.DUCKDUCKGO, description="Search engine to use")


class SearchResult(BaseModel):
    """Model for individual web search results."""
    
    title: str = Field(..., description="Title of the search result")
    link: str = Field(..., description="URL link of the search result")
    snippet: str = Field(default="", description="Brief description or snippet")


class SearchOutput(BaseModel):
    """Output model for web search operations."""
    
    results: List[SearchResult] = Field(..., description="List of search results with titles and links")
    total_found: int = Field(..., description="Total number of results found")
    query: str = Field(..., description="The original search query")
    status: SearchStatus = Field(SearchStatus.SUCCESS, description="Status of the search operation")


def search_web(input: SearchInput) -> SearchOutput:
    """
    Search the web for a query and return the results.
    
    This function performs web searches using DuckDuckGo and extracts
    search results including titles, links, and snippets. It handles
    network errors and parsing issues gracefully.
    
    Args:
        input: SearchInput object containing query and search parameters
        
    Returns:
        SearchOutput: Object containing search results and metadata
        
    Raises:
        requests.RequestException: If the HTTP request fails
        requests.Timeout: If the request times out
        Exception: For any other search or parsing errors
    """
    try:
        if input.search_engine == SearchEngine.DUCKDUCKGO:
            return _search_duckduckgo(input)
        else:
            return SearchOutput(
                results=[],
                total_found=0,
                query=input.query,
                status=SearchStatus.REQUEST_FAILED
            )
            
    except Exception as e:
        return SearchOutput(
            results=[],
            total_found=0,
            query=input.query,
            status=SearchStatus.REQUEST_FAILED
        )


def _search_duckduckgo(input: SearchInput) -> SearchOutput:
    """
    Perform search using DuckDuckGo search engine.
    
    Args:
        input: SearchInput object containing query and search parameters
        
    Returns:
        SearchOutput: Object containing search results and metadata
        
    Raises:
        requests.RequestException: If the HTTP request fails
        requests.Timeout: If the request times out
    """
    url: str = "https://duckduckgo.com/html/"
    params: Dict[str, str] = {"q": input.query}
    headers: Dict[str, str] = {"User-Agent": "Mozilla/5.0"}

    response: requests.Response = requests.get(url, params=params, headers=headers)
    if response.status_code != 200:
        return SearchOutput(
            results=[],
            total_found=0,
            query=input.query,
            status=SearchStatus.REQUEST_FAILED
        )

    try:
        soup: BeautifulSoup = BeautifulSoup(response.text, "html.parser")
        results: List[SearchResult] = []
        
        for result in soup.select(".result__title a")[:input.max_results]:
            title: str = result.get_text().strip()
            link: str = result.get("href", "")
            
            # Extract snippet if available
            snippet: str = ""
            snippet_elem = result.find_next_sibling(".result__snippet")
            if snippet_elem:
                snippet = snippet_elem.get_text().strip()
            
            search_result: SearchResult = SearchResult(
                title=title,
                link=link,
                snippet=snippet
            )
            results.append(search_result)

        return SearchOutput(
            results=results,
            total_found=len(results),
            query=input.query,
            status=SearchStatus.SUCCESS if results else SearchStatus.NO_RESULTS
        )
        
    except Exception as e:
        return SearchOutput(
            results=[],
            total_found=0,
            query=input.query,
            status=SearchStatus.PARSE_ERROR
        )
