from typing import Callable, Any
from pydantic import BaseModel, Field
from pydantic_ai import Agent, RunContext
from data.milvus.indexing import MilvusIndexer

from llm.base import AgentClient
from utils.basetools.faq_tool import create_faq_tool
from utils.basetools.send_email_tool import send_email_tool, EmailToolInput
from data.prompts.company1 import SYSTEM_PROMPT

import chainlit as cl
from data.cache.memory_handler import MessageMemoryHandler



# 1. Định nghĩa schema đầu ra với Callable field
class FuncOutput(BaseModel):
    """Output chứa một hàm nhận int và trả về int."""
    func: Callable[[int], int] = Field(
        ..., 
        description="Một hàm nhận vào int và trả về int, đã được validate là callable"
    )

# 2. Khởi tạo Agent
faq_tool = create_faq_tool(collection_name="company1")

# Create agent with tools
agent = AgentClient(
    system_prompt=SYSTEM_PROMPT,
    tools=[faq_tool]
).create_agent()

# 3. Đăng ký tool, trả về Callable[[int],int]
@agent.tool
def make_multiplier(ctx: RunContext, factor: int) -> FuncOutput:
    """
    Tạo và trả về một hàm multiplier(x) = x * factor.
    """
    def multiplier(x: int) -> int:
        return x * factor

    # Pydantic sẽ kiểm tra multiplier là callable theo annotation phía trên
    return FuncOutput(func=multiplier)

# 4. Ví dụ gọi agent
async def example():
    result = await agent.run(
        "Hãy tạo hàm nhân với 5 rồi gọi nó với x=3.",
    )
    # result.output.func chính là multiplier, có thể gọi tiếp:
    output_model = result.output  # FuncOutput instance
    print(output_model)
