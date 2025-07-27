"""
Text classification module using Gemini API.

This module provides functionality for single-label text classification using Google's Gemini API.
It supports multilingual text classification with configurable labels and temperature settings.
"""

import os
import json
import requests
from typing import Dict, List
from enum import Enum

from pydantic import BaseModel, Field
from dotenv import load_dotenv

load_dotenv()


class ClassificationMode(str, Enum):
    """Enum for classification modes."""
    SINGLE_LABEL = "single_label"
    MULTI_LABEL = "multi_label"


class SearchInput(BaseModel):
    """Input model for text classification requests."""
    query: str = Field(..., description="Text query to be classified")


class SearchOutput(BaseModel):
    """Output model for text classification results."""
    result: str = Field(..., description="The classified label")
    confidence: float = Field(default=0.0, description="Confidence score of the classification")
    mode: ClassificationMode = Field(default=ClassificationMode.SINGLE_LABEL, description="Classification mode used")


class GeminiResponseData(BaseModel):
    """Model for structured Gemini API response data."""
    candidates: List[Dict[str, Dict[str, List[Dict[str, str]]]]]


# Environment configuration
API_KEY: str = os.getenv("GEMINI_API_KEY", "")
if not API_KEY:
    raise RuntimeError("GEMINI_API_KEY environment variable is missing")

ENDPOINT: str = (
    "https://generativelanguage.googleapis.com/v1beta"
    "/models/gemini-2.0-flash:generateContent"
)


def classify_scholarship_http(
    inp: SearchInput,
    labels: List[str],
    *,
    temperature: float = 0.1,
    timeout: int = 30,
) -> SearchOutput:
    """
    Classify text using Gemini API with specified labels.
    
    This function sends a text classification request to the Gemini API and returns
    the most appropriate label from the provided list. The function ensures strong
    typing and proper error handling.
    
    Args:
        inp: SearchInput object containing the query text to classify
        labels: List of possible classification labels (must have at least 2 distinct labels)
        temperature: Controls randomness in the model's response (0.0 to 1.0)
        timeout: Request timeout in seconds
        
    Returns:
        SearchOutput: Object containing the classification result and metadata
        
    Raises:
        ValueError: If labels list is invalid (empty or less than 2 distinct labels)
        RuntimeError: If API response format is unexpected
        requests.RequestException: If API request fails
    """
    if not labels or len(set(labels)) < 2:
        raise ValueError("`labels` must contain at least two distinct strings.")

    labels = [label.strip().lower() for label in labels]

    system_prompt: str = (
        "You are a helpful AI assistant specialised in single‑label text classification.\n"
        "ONLY reply the exact text of **one** label from the following list (case‑insensitive): "
        + ", ".join(labels)
        + "."
    )
    user_prompt: str = f'Question: "{inp.query}"'

    payload: Dict[str, Dict[str, List[Dict[str, str]]] | Dict[str, float]] = {
        "contents": [
            {"role": "user", "parts": [{"text": system_prompt}]},
            {"role": "user", "parts": [{"text": user_prompt}]},
        ],
        "generationConfig": {"temperature": temperature},
    }

    resp = requests.post(
        ENDPOINT,
        params={"key": API_KEY},
        json=payload,
        timeout=timeout,
    )
    resp.raise_for_status()
    data: Dict[str, List[Dict[str, Dict[str, List[Dict[str, str]]]]]] = resp.json()

    try:
        reply_text: str = (
            data["candidates"][0]["content"]["parts"][0]["text"]
            .strip('"\' \n\t\r')
            .lower()
        )
    except (KeyError, IndexError):
        raise RuntimeError(f"Unexpected Gemini response: {json.dumps(data)[:200]}…")

    if reply_text not in labels:
        reply_text = "Undefined"

    return SearchOutput(result=reply_text)
