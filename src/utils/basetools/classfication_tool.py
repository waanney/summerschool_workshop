from __future__ import annotations

import os
from enum import Enum

from pydantic import BaseModel, Field
import instructor
import google.generativeai as genai


os.environ["GOOGLE_API_KEY"] = os.getenv("GOOGLE_API_KEY", "AIzaSyBYOY442tEZdMZO_5jAl4UpDAlXjyFVbWY")  # hoặc dùng .env

# ─────────────────── 2.  Tạo Gemini client & patch bằng Instructor ──────────
genai.configure()


gemini_model = genai.GenerativeModel(model_name="models/gemini-1.5-flash-latest")

client = instructor.from_gemini(
    client=gemini_model,
    mode=instructor.Mode.GEMINI_JSON,       # tự parse JSON → Pydantic
)


class StudentType(str, Enum):
    GIOI = "giỏi"
    KHO_KHAN = "khó khăn"
    QUOC_TE = "quốc tế"

class ClassifyOutput(BaseModel):
    student_type: StudentType = Field(
        description="Một trong: 'giỏi', 'khó khăn', 'quốc tế'"
    )


def classify_scholarship(text: str) -> str:
    prompt = (
        "Bạn là trợ lý học bổng. "
        "Đọc câu hỏi và trả lời **duy nhất** một từ: 'giỏi', 'khó khăn', hoặc 'quốc tế'.\n"
        f"Câu hỏi: \"{text}\""
    )

    result: ClassifyOutput = client.chat.completions.create(
        messages=[{"role": "user", "content": prompt}],
        response_model=ClassifyOutput,
        generation_config={"temperature": 0.1},
    )
    return result.student_type.value