import chainlit as cl
from pydantic_ai import Agent
from pydantic_ai.models.gemini import GeminiModel
from pydantic_ai.providers.google_gla import GoogleGLAProvider
from utils.basetools.testtools import get_current_date
from data.prompts.demo import SYSTEM_PROMT
import os

# Initialize the Gemini model and agent
provider = GoogleGLAProvider(api_key=os.getenv("GEMINI_API_KEY"))
model = GeminiModel('gemini-2.0-flash', provider=provider)
agent = Agent(model=model, system_prompt=SYSTEM_PROMT, tools=[get_current_date])

@cl.on_message
async def main(message: cl.Message):
    """Handle incoming messages and generate responses."""
    # Convert Chainlit message to Gemini-compatible format
    gemini_message = [{
        'role': 'user',
        'content': message.content
    }]
    
    # Run the agent with the formatted message
    response = await agent.run(str(gemini_message))
    await cl.Message(content=str(response.output)).send()
