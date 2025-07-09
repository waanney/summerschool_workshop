from data.milvus.indexing import MilvusIndexer

from pydantic_ai.models.gemini import GeminiModel
from pydantic_ai.providers.google_gla import GoogleGLAProvider
import os

from llm.base import AgentClient
from utils.basetools.faq_tool import create_faq_tool
from utils.basetools.search_in_file_tool import search_in_file
from utils.basetools.send_email_tool import create_send_email_tool
from data.prompts.company2 import SYSTEM_PROMPT

import chainlit as cl
from data.cache.memory_handler import MessageMemoryHandler


# Initialize Milvus indexer (run only once to create collection and index data)
# Comment this out after first run

indexer = MilvusIndexer(collection_name="company2", faq_file="src/data/mock_data/Product_Info_final_make_sense.csv")
indexer.run() 

# Comment this out after first run

# Initialize AI components
provider = GoogleGLAProvider(api_key=os.getenv("GEMINI_API_KEY"))
model = GeminiModel('gemini-2.0-flash', provider=provider)

# Create FAQ tool with custom collection name
faq_tool = create_faq_tool(collection_name="company2")
send_email_tool = create_send_email_tool(to_emails=["dung.phank24@gmail.com"],sender_email="phanthuydung6666@gmail.com", sender_password="Phan12345678@")

# Create agent with tools
agent = AgentClient(
    system_prompt=SYSTEM_PROMPT,
    tools=[search_in_file, faq_tool, send_email_tool]
).create_agent()


# Initialize memory handler
memory_handler = MessageMemoryHandler(max_messages=15)

@cl.on_chat_start
async def start():
    """Initialize chat session"""
    cl.user_session.set("message_count", 0)
    await cl.Message(content="**Welcome to the Product Information Assistant!**").send()

@cl.on_message
async def main(message: cl.Message):
    message_with_context = memory_handler.get_history_message(message.content)
    
    try:
        response = await agent.run(message_with_context)
        memory_handler.store_bot_response(response.output)
        await cl.Message(content=str(response.output)).send()
        
    except Exception as e:
        memory_handler.store_error(e)
        await cl.Message(content=f"**Error:** {str(e)}\n\nPlease try again.").send()
