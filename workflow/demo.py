import os
import chainlit as cl
from pydantic_ai.models.gemini import GeminiModel
from pydantic_ai.providers.google_gla import GoogleGLAProvider
from utils.basetools.faq_tool import faq_tool
from data.prompts.admission_prompt import ADMISSION_PROMPT
from llm.base import AgentClient
import yaml


# Initialize the Gemini model and agent
provider = GoogleGLAProvider(api_key=os.getenv("GEMINI_API_KEY"))
model = GeminiModel('gemini-2.0-flash', provider=provider)

# Single Admission FAQ Agent
agent_client = AgentClient(
    model=model,
    system_prompt=ADMISSION_PROMPT,
    tools=[faq_tool]
)

agent = agent_client.create_agent()

@cl.on_chat_start
async def start():
    """Initialize chat session"""
    await cl.Message(
        content="🎓 **Chào mừng đến với Hệ thống FAQ Tuyển sinh!**\n\n"
    ).send()

@cl.on_message
async def main(message: cl.Message):
    """Handle incoming messages and generate responses."""
    # Single agent handles all queries
    response = await agent.run(message.content)
    await cl.Message(content=str(response.output)).send()