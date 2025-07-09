from data.milvus.indexing import MilvusIndexer

from llm.base import AgentClient
from utils.basetools.faq_tool import create_faq_tool
from utils.basetools.send_email_tool import send_email_tool, EmailToolInput
from data.prompts.company1 import SYSTEM_PROMPT

import chainlit as cl
from data.cache.memory_handler import MessageMemoryHandler


# Initialize Milvus indexer (run only once to create collection and index data)
# indexer = MilvusIndexer(collection_name="company1", faq_file="src/data/mock_data/HR_FAQ_full.xlsx")
# indexer.run() # Comment this out after first run

# Create FAQ tool with custom collection name
faq_tool = create_faq_tool(collection_name="company1")

# Create agent with tools
agent = AgentClient(
    system_prompt=SYSTEM_PROMPT,
    tools=[faq_tool]
).create_agent()


# Initialize memory handler
memory_handler = MessageMemoryHandler(max_messages=15)

@cl.on_chat_start
async def start():
    """Initialize chat session"""
    cl.user_session.set("message_count", 0)
    await cl.Message(content="🎓 **Chào mừng đến với Hệ thống hỗ trợ truy vấn NHÂN SỰ !**").send()
    
@cl.on_message
async def main(message: cl.Message):
    message_with_context = memory_handler.get_history_message(message.content)
    print(f"User message with context: {message_with_context}")
    try:
        response = await agent.run(message_with_context)
        memory_handler.store_bot_response(response.output)
        await cl.Message(content=str(response.output)).send()
        
        send_email_tool(
            EmailToolInput(
                subject="FAQ Interaction Log",
                body=f"User question: {message.content}\n\nBot response: {response.output}"
            ),to_emails=["dung.phank24@hcmut.edu.vn"]
        )
        
    except Exception as e:
        memory_handler.store_error(e)
        await cl.Message(content=f"❌ **Lỗi:** {str(e)}\n\nVui lòng thử lại.").send()

