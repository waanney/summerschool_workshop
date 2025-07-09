from data.milvus.indexing import MilvusIndexer
from pydantic_ai.models.gemini import GeminiModel
from pydantic_ai.providers.google_gla import GoogleGLAProvider
import os
from llm.base import AgentClient
from utils.basetools.faq_tool import create_faq_tool
from utils.basetools.send_email_tool import create_send_email_tool
from data.prompts.mini_qa_agent_prompt import SYSTEM_PROMPT
import chainlit as cl
from data.cache.memory_handler import MessageMemoryHandler

# 1. Initialize Milvus indexer
# This should be run only once to create the collection and index the data.
# After the first run, you can comment it out.
indexer = MilvusIndexer(
    collection_name="mini_qa_agent",
    faq_file="src/data/mock_data/admission_faq_large.csv"
)
indexer.run()

# 2. Initialize AI components
provider = GoogleGLAProvider(api_key=os.getenv("GEMINI_API_KEY"))
model = GeminiModel('gemini-2.0-flash', provider=provider)

# 3. Create tools
faq_tool = create_faq_tool(collection_name="mini_qa_agent")
send_email_tool = create_send_email_tool(to_emails=["admin@example.com"])

# 4. Create agent
agent = AgentClient(
    system_prompt=SYSTEM_PROMPT,
    tools=[faq_tool, send_email_tool]
).create_agent()

# 5. Initialize memory handler
memory_handler = MessageMemoryHandler(max_messages=15)

@cl.on_chat_start
async def start():
    """Initialize chat session"""
    await cl.Message(
        content="""Chào mừng bạn đến với Mini QA Agent!

Tôi có thể giúp bạn trả lời các câu hỏi về tuyển sinh. Hãy đặt câu hỏi cho tôi."""
    ).send()

@cl.on_message
async def main(message: cl.Message):
    """Handle incoming messages"""
    message_with_context = memory_handler.get_history_message(message.content)
    
    try:
        response = await agent.run(message_with_context)
        memory_handler.store_bot_response(response.output)
        await cl.Message(content=str(response.output)).send()
        
    except Exception as e:
        memory_handler.store_error(e)
        await cl.Message(content=f"Đã có lỗi xảy ra: {str(e)}\n\nVui lòng thử lại.").send()
