from pydantic_ai import Agent
from typing import List, Callable
from pydantic_ai.models.gemini import GeminiModel
from pydantic_ai.providers.google_gla import GoogleGLAProvider
import os
from data.cache.redis_cache import ShortTermMemory

provider = GoogleGLAProvider(api_key=os.getenv("GEMINI_API_KEY"))
model = GeminiModel("gemini-2.0-flash", provider=provider)
session_manager = ShortTermMemory(max_messages=15)


class AgentClient:
    def __init__(
        self, system_prompt: str, tools: List[Callable], model: GeminiModel = model
    ):
        self.model = model
        self.system_prompt = system_prompt
        self.tools = tools

    def create_agent(self) -> Agent:
        """Creates and returns a PydanticAI Agent instance."""
        return Agent(
            model=self.model, system_prompt=self.system_prompt, tools=self.tools
        )
