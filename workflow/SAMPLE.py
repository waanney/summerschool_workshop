from data.milvus.indexing import MilvusIndexer
import os
from llm.base import AgentClient
from utils.basetools.faq_tool import create_faq_tool
from pydantic_ai.models.gemini import GeminiModel
from pydantic_ai.providers.google_gla import GoogleGLAProvider

from data.cache.memory_handler import MessageMemoryHandler

import chainlit as cl

from utils.basetools.send_email_tool import send_email_tool, EmailToolInput

# Initialize Milvus indexer (run only once to create collection and index data)
# Comment this out after first run
# Replace "___________" with your collection name and FAQ file path
indexer = MilvusIndexer(collection_name="_______", faq_file="___________________")  

# Initialize model and provider
provider = GoogleGLAProvider(api_key=os.getenv("GEMINI_API_KEY"))
model = GeminiModel('gemini-2.0-flash', provider=provider)

# Initialize your tool 
#---------------------------------------------

#---------------------------------------------

# Initialize agent with tools
agent = AgentClient(
    model=model,
    system_prompt="__________________________",  # Replace with your system prompt
    tools=[] # Replace with your tools if any, e.g., [faq_tool]
).create_agent()

@cl.on_message
async def main(message: cl.Message):    
    # YOUR LOGIC HERE
    response = await agent.run((message.content))
    await cl.Message(content=str(response.output)).send()
