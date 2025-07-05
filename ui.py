import asyncio
import chainlit as cl
from src.llm.base import AgentManager

manager = AgentManager()  

@cl.on_message
async def on_message(message: cl.Message):
    response = await manager.handle_user_query(message.content)
    message = cl.Message(content=response, author="AI Model")
    await message.send()

@cl.on_stop
def on_stop():
    print("Application stopped.")
