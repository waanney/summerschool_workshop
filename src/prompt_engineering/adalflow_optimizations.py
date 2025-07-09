from adalflow import Generator, Parameter, ParameterType
from adalflow.components.model_client.google_client import GoogleGenAIClient
import os
from dotenv import load_dotenv

load_dotenv()
# --- Khởi tạo client từ AdalFlow ---
client = GoogleGenAIClient(api_key=os.getenv("GEMINI_API_KEY"))

# --- Prompt được tối ưu tự động ---
system_prompt = Parameter(
    data="You are a helpful assistant. Explain step by step then summarize the answer.",
    param_type=ParameterType.PROMPT,
    requires_opt=True,
)

template = """
<SYS>
{{system_prompt}}
</SYS>

User: {{user_query}}
"""

# --- Model kwargs: nhớ chỉ định model name ---
model_kwargs = {
    "model": "gemini-2.0-flash",
    "temperature": 0.7,  # tùy chỉnh nếu cần
    "max_output_tokens": 512,  # giới hạn token
}

# --- Tạo Generator ---
generator = Generator(
    model_client=client,
    model_kwargs=model_kwargs,
    template=template,
    prompt_kwargs={"system_prompt": system_prompt},
)


# --- Hàm gọi agent ---
def ask_agent(user_query: str) -> str:
    output = generator(prompt_kwargs={"user_query": user_query})
    return output.raw_response  # hoặc .data / .raw_response


# --- Thử chạy ---
if __name__ == "__main__":
    while True:
        q = input("Bạn hỏi gì: ")
        if not q:
            break
        print("Gemini Agent:", ask_agent(q))
