import os
import chainlit as cl
from pydantic_ai.models.gemini import GeminiModel
from pydantic_ai.providers.google_gla import GoogleGLAProvider
from utils.basetools.search_web_tool import search_web
from utils.basetools.calculator_tool import calculate_expression, basic_math, trigonometry, logarithm, calculator_memory
from data.prompts.admission_prompt import ADMISSION_PROMPT
from data.cache.redis_cache import ShortTermMemory
from llm.base import AgentClient



# Initialize the Gemini model and agent
provider = GoogleGLAProvider(api_key=os.getenv("GEMINI_API_KEY"))
model = GeminiModel('gemini-2.0-flash', provider=provider)

# Initialize memory for conversation history
memory = ShortTermMemory(max_messages=10)  # Lưu tối đa 10 tin nhắn

# Single Admission FAQ Agent with Calculator
agent_client = AgentClient(
    model=model,
    system_prompt=ADMISSION_PROMPT,
    tools=[search_web, calculate_expression, basic_math, trigonometry, logarithm, calculator_memory]
)

agent = agent_client.create_agent()

@cl.on_chat_start
async def start():
    """Initialize chat session"""
    # Tạo session key duy nhất cho mỗi user
    session_key = f"user_{cl.user_session.get('id', 'default')}_session"
    cl.user_session.set("session_key", session_key)
    
    await cl.Message(
        content="🎓 **Chào mừng đến với Hệ thống FAQ Tuyển sinh với Calculator!**\n\n"
                "Tôi có thể giúp bạn:\n"
                "- Trả lời các câu hỏi về tuyển sinh\n"
                "- Thực hiện các phép tính toán học\n"
                "- Tìm kiếm thông tin trên web\n"
                "- Nhớ lịch sử cuộc trò chuyện của chúng ta\n\n"
                "Hãy đặt câu hỏi của bạn!"
    ).send()

@cl.on_message
async def main(message: cl.Message):
    """Handle incoming messages and generate responses with memory."""
    session_key = cl.user_session.get("session_key")
    if not session_key:
        # Fallback nếu không có session_key
        session_key = "default_session"
        cl.user_session.set("session_key", session_key)
    
    # Kiểm tra lệnh đặc biệt để xóa memory
    if message.content.lower().strip() in ['/clear', '/reset', 'xóa lịch sử', 'clear memory']:
        memory.delete(session_key)
        await cl.Message(
            content="🗑️ **Đã xóa lịch sử cuộc trò chuyện!**\n\nChúng ta có thể bắt đầu cuộc trò chuyện mới."
        ).send()
        return
    
    # Lưu tin nhắn của user vào memory
    user_message = f"User: {message.content}"
    memory.store(session_key, user_message)
    
    # Lấy lịch sử conversation
    conversation_history = memory.retrieve(session_key)
    
    # Tạo context với lịch sử cuộc trò chuyện
    context_with_history = ""
    if len(conversation_history) > 1:  # Nếu có lịch sử
        context_with_history = "\n--- Lịch sử cuộc trò chuyện ---\n"
        # Reverse để hiển thị theo thứ tự thời gian (cũ -> mới)
        for msg in reversed(conversation_history[1:]):  # Bỏ qua tin nhắn hiện tại
            context_with_history += f"{msg}\n"
        context_with_history += "--- Hết lịch sử ---\n\n"
    
    # Tạo prompt với context
    full_message = f"{context_with_history}Current question: {message.content}"
    
    # Gọi agent với context đầy đủ
    response = await agent.run(full_message)
    
    # Lưu response của bot vào memory
    bot_message = f"Bot: {response.output}"
    memory.store(session_key, bot_message)
    
    await cl.Message(content=str(response.output)).send()