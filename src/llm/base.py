from pydantic_ai import Agent
from typing import List, Callable
import asyncio

class AgentClient:
    def __init__(self, model, system_prompt: str, tools: List[Callable]):
        self.model = model
        self.system_prompt = system_prompt
        self.tools = tools

    def create_agent(self):
        """Creates and returns a PydanticAI Agent instance."""
        return Agent(
            model=self.model,
            system_prompt=self.system_prompt,
            tools=self.tools
        )


