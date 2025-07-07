from utils.basetools.faq_tool import faq_tool
from utils.basetools.search_in_file_tool import search_in_file 
from utils.basetools.classfication_tool import classify_scholarship_http 
from data.prompts.company4_demo_prompt import COMPANY4_DEMO
from llm.base import AgentClient
from data.cache.redis_cache import ShortTermMemory
import chainlit as cl





session_manager = ShortTermMemory()

agent1 = AgentClient(
    system_prompt=COMPANY4_DEMO,
    tools =[search_in_file] 
).create_agent()


agent_manager = AgentClient(
    system_prompt=COMPANY4_DEMO,
    tools = [classify_scholarship_http]
).create_agent()

@cl.on_message
async def on_message(message: cl.Message):
    response = await handle_user_query(agent_manager,message.content)
    message = cl.Message(content=response, author="AI Model")
    await message.send()

@cl.on_stop
def on_stop():
    print("Application stopped.")
