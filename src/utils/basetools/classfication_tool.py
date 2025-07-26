import os
import json
import requests
from typing import Any, Dict, List

from pydantic import BaseModel, Field
from dotenv import load_dotenv

load_dotenv()


class SearchInput(BaseModel):
    query: str = Field(..., description="Search query")


class SearchOutput(BaseModel):
    result: str = Field(..., description="Identifying the label")


API_KEY: str | None = os.getenv("GEMINI_API_KEY")
if not API_KEY:
    raise RuntimeError("GEMINI_API_KEY env var is missing")

ENDPOINT = (
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

    if not labels or len(set(labels)) < 2:
        raise ValueError("`labels` must contain at least two distinct strings.")

    labels = [label.strip().lower() for label in labels]

    system_prompt = (
        "You are a helpful AI assistant specialised in single‑label text classification.\n"
        "ONLY reply the exact text of **one** label from the following list (case‑insensitive): "
        + ", ".join(labels)
        + "."
    )
    user_prompt = f'Câu hỏi: "{inp.query}"'

    payload: Dict[str, Any] = {
        "contents": [
            {"role": "user", "parts": [{"text": system_prompt}]},
            {"role": "user", "parts": [{"text": user_prompt}]},
        ],
        "generationConfig": {"temperature": 0.1},
    }

    resp = requests.post(
        ENDPOINT,
        params={"key": API_KEY},
        json=payload,
        timeout=timeout,
    )
    resp.raise_for_status()
    data = resp.json()

    try:
        reply_text: str = (
            data["candidates"][0]["content"]["parts"][0]["text"]
            .strip("“”\"' \n\t\r")
            .lower()
        )
    except (KeyError, IndexError):
        raise RuntimeError(f"Unexpected Gemini response: {json.dumps(data)[:200]}…")

    if reply_text not in labels:
        reply_text = "Undefined"

    return SearchOutput(result=reply_text)
