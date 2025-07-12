from data.milvus.indexing import MilvusIndexer
import os
from llm.base import AgentClient
from pydantic_ai.models.gemini import GeminiModel
from pydantic_ai.providers.google_gla import GoogleGLAProvider

from data.cache.memory_handler import MessageMemoryHandler

import chainlit as cl

from utils.basetools import *

# Initialize Milvus indexer (run only once to create collection and index data)
# Comment this out after first run
# Replace "___________" with your collection name and FAQ file path
indexer = MilvusIndexer(collection_name="company1", faq_file="src/data/mock_data/HR_FAQ.xlsx")
indexer.run()
# Initialize model and provider
provider = GoogleGLAProvider(api_key=os.getenv("GEMINI_API_KEY"))
model = GeminiModel('gemini-2.0-flash', provider=provider)

# Initialize your tool 
#---------------------------------------------
faq_tool = create_faq_tool(collection_name="company1")
#---------------------------------------------

# Initialize agent with tools
agent = AgentClient(
    model=model,
    system_prompt="You are an intelligent virtual assistant. Please use `faq_tool` to search user question and answer.",  # Replace with your system prompt
    tools=[faq_tool] # Replace with your tools if any, e.g., [faq_tool]
).create_agent()

@cl.on_message
async def main(message: cl.Message):    
    # YOUR LOGIC HERE
    response = await agent.run((message.content))
    await cl.Message(content=str(response.output)).send()

    send_email_tool(
        EmailToolInput(
            subject="FaQ Question Received",
            body=f"Received question: {message.content}\nResponse: {response.output}"
        ), to_emails=["dung.phank24@hcmut.edu.vn"]
    )