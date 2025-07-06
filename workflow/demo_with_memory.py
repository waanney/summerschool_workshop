import os
import chainlit as cl
from pydantic_ai.models.gemini import GeminiModel
from pydantic_ai.providers.google_gla import GoogleGLAProvider
from utils.basetools.faq_tool import faq_tool
from utils.basetools.calculator_tool import calculate_expression, basic_math, trigonometry, logarithm, calculator_memory
from data.prompts.admission_prompt import ADMISSION_PROMPT
from data.cache.redis_cache import ShortTermMemory
from llm.base import AgentClient

# Initialize components
provider = GoogleGLAProvider(api_key=os.getenv("GEMINI_API_KEY"))
model = GeminiModel('gemini-2.0-flash', provider=provider)
session_manager = ShortTermMemory(max_messages=15)

# Enhanced Admission FAQ Agent with Calculator and Memory
agent = AgentClient(
    model=model,
    system_prompt=ADMISSION_PROMPT,
    tools=[faq_tool, calculate_expression, basic_math, trigonometry, logarithm, calculator_memory]
).create_agent()

@cl.on_chat_start
async def start():
    """Initialize chat session"""
    cl.user_session.set("message_count", 0)
    await cl.Message(content="🎓 **Chào mừng đến với Hệ thống FAQ Tuyển sinh thông minh với Memory!**").send()

@cl.on_message
async def main(message: cl.Message):
    """Handle user messages with memory"""
    session_key = session_manager.get_session_key()
    session_manager.update_message_count()
    
    # Build context with history BEFORE storing current user message
    context = session_manager.get_history_context(session_key)
    full_message = f"{context}CURRENT REQUEST: {message.content}"
    
    # Store user message AFTER getting history
    session_manager.store_user_message(session_key, message.content)
    
    try:
        response = await agent.run(full_message)
        session_manager.store_bot_message(session_key, response.output)
        await cl.Message(content=str(response.output)).send()
        
    except Exception as e:
        session_manager.store_error_message(session_key, e)
        await cl.Message(content=f"❌ **Lỗi:** {str(e)}\n\nVui lòng thử lại.").send()
