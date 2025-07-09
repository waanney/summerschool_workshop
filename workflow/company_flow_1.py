from data.milvus.indexing import MilvusIndexer

from llm.base import AgentClient
from utils.basetools.faq_tool import create_faq_tool

from data.cache.memory_handler import MessageMemoryHandler

import chainlit as cl

from utils.basetools.send_email_tool import send_email_tool, EmailToolInput

# Initialize Milvus indexer (run only once to create collection and index data)
indexer = MilvusIndexer(collection_name="company1", faq_file="src/data/mock_data/HR_FAQ_full.xlsx")
indexer.run() # Comment this out after first run

faq_tool = create_faq_tool(collection_name="company1")

agent = AgentClient(
    system_prompt="You are a helpful assistant for HR queries. Answer questions based on the provided FAQ data. Use the FAQ tool to find relevant answers.",
    tools=[faq_tool] 
).create_agent()


memory_handler = MessageMemoryHandler(max_messages=15)

@cl.on_message
async def main(message: cl.Message):    
    # YOUR LOGIC HERE
    message_with_context = memory_handler.get_history_message(message.content)
    response = await agent.run(message_with_context)
    await cl.Message(content=str(response.output)).send()
    memory_handler.store_bot_response(response.output)
    
    send_email_tool(
        EmailToolInput(
            subject="FAQ Interaction Log",
            body=f"User question: {message.content}\n\nBot response: {response.output}"
        ), to_emails=["dung.phank24@hcmut.edu.vn"]
    )