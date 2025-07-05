from utils.basetools.testtools import get_current_date
from llm.base import AgentClient
import asyncio
from pydantic_ai.models.gemini import GeminiModel 
from pydantic_ai.providers.google_gla import GoogleGLAProvider
from dotenv import load_dotenv
import os
from data.prompts.demo import SYSTEM_PROMT 

load_dotenv()

provider = GoogleGLAProvider(api_key= os.getenv("GEMINI_API_KEY"))
model = GeminiModel('gemini-2.0-flash', provider=provider)

agent_client = AgentClient(
    model = model,
    system_prompt=SYSTEM_PROMT,
    tools=[get_current_date]
)

agent1 = agent_client.create_agent()
agent2= agent_client.create_agent()
# Use the agent to run a task
async def main():
    async with agent1.run_stream("What is today's date?") as response:
        output = await response.get_output()
        print(output)

    async with agent2.run_stream("What is today's date?") as response:
        output = await response.get_output()
        print(output)

# Run the async main function
asyncio.run(main())
