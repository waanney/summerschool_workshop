📘 PydanticAI Tool – search_tool

Tool search_tool cung cấp chức năng tìm kiếm tài liệu dựa trên truy vấn của người dùng, trả về các đoạn văn bản có liên quan. Tool này được xây dựng để tích hợp dễ dàng với PydanticAI Agent.
🧩 Cấu trúc file

Dự án được tổ chức theo cấu trúc sau:

your_project/
├── tools/
│   └── search_tool.py  # Chứa định nghĩa của search_tool
└── main.py             # File chính để chạy agent

⚙️ Cài đặt

    Tạo file requirements.txt với nội dung sau:

    pydantic-ai
    pydantic

    Cài đặt các thư viện cần thiết bằng lệnh:

    pip install -r requirements.txt

🚀 Cách sử dụng

Để thực thi agent và sử dụng search_tool, bạn chỉ cần chạy file main.py.

Nội dung tools/search_tool.py:

from typing import List
from pydantic import BaseModel, Field
from pydantic_ai import Agent, RunContext

# Khởi tạo agent với system prompt
agent = Agent(
    'openai:gpt-4o',
    system_prompt='Bạn là trợ lý hỗ trợ tìm tài liệu.'
)

class SearchInput(BaseModel):
    """Định nghĩa cấu trúc dữ liệu đầu vào cho tool."""
    query: str = Field(..., description="Câu truy vấn tìm kiếm.")
    k: int = Field(3, ge=1, le=10, description="Số lượng kết quả tối đa.")

class SearchOutput(BaseModel):
    """Định nghĩa cấu trúc dữ liệu đầu ra cho tool."""
    docs: List[str] = Field(..., description="Danh sách tài liệu liên quan.")

def do_search(query: str, k: int) -> List[str]:
    """Hàm logic thực hiện tìm kiếm (mô phỏng)."""
    return [f"Tài liệu liên quan đến '{query}' #{i+1}" for i in range(k)]

@agent.tool
def search_tool(ctx: RunContext[str], inp: SearchInput) -> SearchOutput:
    """
    Đăng ký hàm `search_tool` với agent.
    PydanticAI sẽ tự động validate input `inp` theo schema `SearchInput`
    và đảm bảo output tuân thủ schema `SearchOutput`.
    """
    return SearchOutput(docs=do_search(inp.query, inp.k))

Nội dung main.py:

from tools.search_tool import agent as search_agent

if __name__ == "__main__":
    # Agent sẽ tự động hiểu yêu cầu, gọi tool `search_tool`
    # và validate dữ liệu vào/ra.
    resp = search_agent.run_sync("Tìm tài liệu về AI")
    print(resp.output.docs)

Chạy ứng dụng:

python main.py

Kết quả mong đợi:

["Tài liệu liên quan đến 'Tìm tài liệu về AI' #1", "Tài liệu liên quan đến 'Tìm tài liệu về AI' #2", "Tài liệu liên quan đến 'Tìm tài liệu về AI' #3"]

💡 Giải thích & Best Practices

    @agent.tool: Decorator này dùng để đăng ký một hàm như một "tool" cho agent. PydanticAI sẽ tự động xử lý việc validate dữ liệu đầu vào và đầu ra dựa trên các Pydantic model được cung cấp.

    SearchInput & SearchOutput: Việc định nghĩa rõ ràng cấu trúc dữ liệu giúp agent hiểu và truyền thông tin một cách chính xác. Đây là một trong những ưu điểm lớn nhất của Pydantic.

    Validation: Các ràng buộc trong Field (ví dụ: ge=1, le=10) giúp đảm bảo tính toàn vẹn và an toàn của dữ liệu, đặc biệt khi nhận đầu vào từ người dùng hoặc các hệ thống bên ngoài.

    Kiểm thử nhanh: Sử dụng agent.run_sync(...) là một cách hiệu quả để kiểm tra xem tool có hoạt động đúng như mong đợi hay không trước khi tích hợp vào một hệ thống lớn hơn.

🔧 Mở rộng

Bạn có thể dễ dàng thêm các tool khác (ví dụ: tool tính toán, gọi API, truy vấn cơ sở dữ liệu) bằng cách làm theo các bước sau:

    Tạo một file tool mới trong thư mục tools/.

    Định nghĩa các BaseModel cho Input và Output.

    Viết hàm logic để xử lý tác vụ.

    Sử dụng decorator @agent.tool hoặc @agent.tool_plain để đăng ký tool với agent.

    Import và sử dụng agent trong main.py hoặc bất kỳ đâu bạn cần.
