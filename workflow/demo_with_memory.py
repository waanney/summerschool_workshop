from llm.base import AgentClient
from data.cache.redis_cache import ShortTermMemory
from handlers.ui_handlers import create_chat_handlers 
from utils.basetools.send_email_tool import send_email_tool

session_manager = ShortTermMemory()
agent = AgentClient(
    system_prompt="You are a excellent assistant, who can help everything that users require",
    tools=[send_email_tool]
).create_agent()

create_chat_handlers(session_manager, agent)
