from pydantic_ai import Agent
from typing import List, Callable
# Load environment variables from .env file

class AgentClient:
    def __init__(self,model, system_prompt: str, tools: List[Callable]):
        self.model_name = model
        self.system_prompt = system_prompt
        self.tools = tools

    def create_agent(self):
        """Creates and returns a PydanticAI Agent instance."""
        return Agent(
            model=self.model_name,
            system_prompt=self.system_prompt,
            tools=self.tools
        )
    










