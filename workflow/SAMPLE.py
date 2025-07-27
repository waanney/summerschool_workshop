from data.milvus.indexing import MilvusIndexer
import os
from llm.base import AgentClient
from pydantic_ai.models.gemini import GeminiModel
from pydantic_ai.providers.google_gla import GoogleGLAProvider

import chainlit as cl

from utils.basetools.faq_tool import create_faq_tool
from utils.basetools.send_email_tool import send_email_tool, EmailToolInput
from data.prompts.mini_qa_agent_prompt import SYSTEM_PROMPT
from data.cache.memory_handler import MessageMemoryHandler


# Initialize Milvus indexer (run only once to create collection and index data)
# Comment this out after first run
# Replace "___________" with your collection name and FAQ file path
indexer = MilvusIndexer(collection_name="company1", faq_file="src/data/mock_data/HR_FAQ.xlsx")
indexer.run()
# Initialize model and provider
provider = GoogleGLAProvider(api_key=os.getenv("GEMINI_API_KEY"))
model = GeminiModel('gemini-2.0-flash', provider=provider)

# Initialize your tools
# ---------------------------------------------
faq_tool = create_faq_tool(collection_name="company1")
# ---------------------------------------------

# Initialize agent with tools
agent = AgentClient(
    model=model,
    system_prompt=SYSTEM_PROMPT,
    tools=[faq_tool]
).create_agent()

memory_handler = MessageMemoryHandler()

@cl.on_chat_start
async def start():
    """Initialize chat session"""
    cl.user_session.set("message_count", 0)
    await cl.Message(content="🎓 **Welcome to the HR Query Support System!**").send()


@cl.on_message
async def main(message: cl.Message):
    # YOUR LOGIC HERE
    message_with_history = memory_handler.get_history_message(message.content)
    response = await agent.run((message_with_history))
    memory_handler.store_bot_response(response.output)
    
    await cl.Message(content=str(response.output)).send()

 
