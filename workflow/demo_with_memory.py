from utils.basetools.faq_tool import faq_tool
from utils.basetools.calculator_tool import calculate_expression, basic_math, trigonometry, logarithm, calculator_memory
from data.prompts.admission_prompt import ADMISSION_PROMPT
from llm.base import AgentClient
from data.cache.redis_cache import ShortTermMemory
from handlers.ui_handlers import create_chat_handlers 
from utils.basetools.file_reading_tool import read_file_tool
from utils.basetools.merge_files_tool import merge_files_tool
session_manager = ShortTermMemory()
agent = AgentClient(
    system_prompt=ADMISSION_PROMPT,
    tools=[faq_tool, calculate_expression, basic_math, trigonometry, logarithm, calculator_memory, read_file_tool, merge_files_tool]
).create_agent()

create_chat_handlers(session_manager, agent)
