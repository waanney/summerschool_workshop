import os, requests, json
from enum import Enum
from typing import Dict, Any
from pydantic import BaseModel, Field
from dotenv import load_dotenv

load_dotenv()


# ---------- Schemas ----------
class StudentType(str, Enum):
    GIOI = "giỏi"
    KHO_KHAN = "khó khăn"
    QUOC_TE = "quốc tế"


class SearchInput(BaseModel):
    query: str = Field(..., description="Search the query")


class SearchOutput(BaseModel):
    results: str = Field(..., description="Determining the student type")


# ---------- Gemini REST call ----------
API_KEY = os.getenv("GEMINI_API_KEY")
if not API_KEY:
    raise RuntimeError("GEMINI_API_KEY env var is missing")

ENDPOINT = (
    "https://generativelanguage.googleapis.com/v1beta"
    "/models/gemini-2.0-flash:generateContent"
)


def classify_scholarship_http(inp: SearchInput) -> SearchOutput:
    # 1. Build prompt
    system_prompt = (
        "Bạn là trợ lý học bổng.\n"
        "Trả lời **duy nhất** một từ: giỏi, khó khăn, hoặc quốc tế."
    )
    user_prompt = f'Câu hỏi: "{inp.query}"'

    payload: Dict[str, Any] = {
        "contents": [
            {"role": "user", "parts": [{"text": system_prompt}]},
            {"role": "user", "parts": [{"text": user_prompt}]},
        ],
        "generationConfig": {"temperature": 0.1},
    }

    # 2. POST to Gemini REST
    resp = requests.post(
        ENDPOINT,
        params={"key": API_KEY},
        json=payload,
        timeout=30,
    )
    resp.raise_for_status()
    data = resp.json()

    # 3. Extract model reply
    try:
        reply_text: str = data["candidates"][0]["content"]["parts"][0]["text"].strip()
    except (KeyError, IndexError):
        raise RuntimeError(f"Unexpected Gemini response: {json.dumps(data)[:200]}…")

    # Optional: normalise
    reply_text = reply_text.lower().strip("“”\"' ")

    # 4. Validate & return
    if reply_text not in StudentType._value2member_map_:
        reply_text = "không thể xác định"  # or any default / error value

    return SearchOutput(results=reply_text)
