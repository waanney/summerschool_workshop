# Hướng dẫn sử dụng nhanh

## Demo đầu tiên

### 1. Chuẩn bị dữ liệu

Trước tiên, hãy đảm bảo bạn có file CSV hoặc Excel chứa câu hỏi và câu trả lời:

```csv
Question,Answer
"How to apply for scholarship?","You can apply for scholarship through our online portal..."
"What are the admission requirements?","The admission requirements include..."
```

### 2. Tạo một FAQ Agent đơn giản

```python
# demo_faq_agent.py
from data.milvus.indexing import MilvusIndexer
from llm.base import AgentClient
from pydantic_ai.models.gemini import GeminiModel
from pydantic_ai.providers.google_gla import GoogleGLAProvider
from utils.basetools import create_faq_tool
import os
import chainlit as cl

# Bước 1: Index dữ liệu FAQ (chỉ chạy 1 lần)
indexer = MilvusIndexer(
    collection_name="my_faq_collection",
    faq_file="src/data/mock_data/admission_faq_large.csv"
)
indexer.run()

# Bước 2: Tạo model và agent
provider = GoogleGLAProvider(api_key=os.getenv("GEMINI_API_KEY"))
model = GeminiModel('gemini-2.0-flash', provider=provider)

# Bước 3: Tạo FAQ tool
faq_tool = create_faq_tool(collection_name="my_faq_collection")

# Bước 4: Tạo agent
agent = AgentClient(
    model=model,
    system_prompt="You are a helpful assistant. Use the FAQ tool to answer user questions.",
    tools=[faq_tool]
).create_agent()

# Bước 5: Chainlit interface
@cl.on_message
async def main(message: cl.Message):
    response = await agent.run(message.content)
    await cl.Message(content=str(response.output)).send()
```

### 3. Chạy demo

```bash
chainlit run demo_faq_agent.py
```

## Các ví dụ sử dụng

### 1. FAQ Agent với Memory

```python
# demo_with_memory.py
from data.cache.memory_handler import MessageMemoryHandler
from llm.base import AgentClient
from utils.basetools import create_faq_tool
import chainlit as cl

# Khởi tạo memory handler
memory_handler = MessageMemoryHandler(max_messages=10)

# Tạo agent với FAQ tool
faq_tool = create_faq_tool(collection_name="my_faq")
agent = AgentClient(
    model=model,
    system_prompt="You are a helpful assistant with memory. Use FAQ tool to answer questions.",
    tools=[faq_tool]
).create_agent()

@cl.on_message
async def main(message: cl.Message):
    # Lấy message với context từ memory
    full_message = memory_handler.get_history_message(message.content)
    
    # Chạy agent
    response = await agent.run(full_message)
    
    # Lưu response vào memory
    memory_handler.store_bot_response(str(response.output))
    
    await cl.Message(content=str(response.output)).send()
```

### 2. Multi-tool Agent

```python
# demo_multi_tool.py
from utils.basetools import (
    create_faq_tool,
    http_tool,
    create_send_email_tool,
    calculate
)

# Tạo các tools
faq_tool = create_faq_tool(collection_name="my_faq")
email_tool = create_send_email_tool(
    to_emails=["admin@example.com"],
    sender_email=None,  # Sẽ lấy từ env
    sender_password=None
)

# Tạo agent với nhiều tools
agent = AgentClient(
    model=model,
    system_prompt="""You are a multi-functional assistant. You can:
    1. Answer FAQ questions using faq_tool
    2. Send emails using email_tool
    3. Perform calculations using calculate
    4. Make HTTP requests using http_tool
    """,
    tools=[faq_tool, email_tool, calculate, http_tool]
).create_agent()

@cl.on_message
async def main(message: cl.Message):
    response = await agent.run(message.content)
    await cl.Message(content=str(response.output)).send()
```

### 3. Custom Tool Agent

```python
# demo_custom_tool.py
from pydantic import BaseModel, Field
from typing import List

# Tạo custom tool
class WeatherInput(BaseModel):
    city: str = Field(..., description="City name")
    country: str = Field("VN", description="Country code")

class WeatherOutput(BaseModel):
    temperature: float = Field(..., description="Temperature in Celsius")
    description: str = Field(..., description="Weather description")

def weather_tool(input: WeatherInput) -> WeatherOutput:
    # Giả lập weather API call
    return WeatherOutput(
        temperature=25.5,
        description=f"Sunny weather in {input.city}, {input.country}"
    )

# Tạo agent với custom tool
agent = AgentClient(
    model=model,
    system_prompt="You are a weather assistant. Use weather_tool to get weather information.",
    tools=[weather_tool]
).create_agent()

@cl.on_message
async def main(message: cl.Message):
    response = await agent.run(message.content)
    await cl.Message(content=str(response.output)).send()
```

## Tạo collection mới

### 1. Với dữ liệu CSV

```python
# create_collection_csv.py
from data.milvus.indexing import MilvusIndexer

# Tạo indexer
indexer = MilvusIndexer(
    collection_name="my_new_collection",
    faq_file="path/to/your/data.csv"
)

# Chạy indexing
indexer.run()
print("Collection created successfully!")
```

### 2. Với dữ liệu Excel

```python
# create_collection_excel.py
from data.milvus.indexing import MilvusIndexer

# Tạo indexer cho Excel file
indexer = MilvusIndexer(
    collection_name="my_excel_collection",
    faq_file="path/to/your/data.xlsx"
)

# Chạy indexing
indexer.run()
print("Excel collection created successfully!")
```

### 3. Với dữ liệu tùy chỉnh

```python
# create_collection_custom.py
from data.milvus.milvus_client import MilvusClient
from data.embeddings.embedding_engine import EmbeddingEngine

# Dữ liệu tùy chỉnh
questions = [
    "What is Python?",
    "How to use AI?",
    "What is machine learning?"
]

answers = [
    "Python is a programming language.",
    "AI can be used for automation.",
    "Machine learning is a subset of AI."
]

# Tạo embeddings
embedding_engine = EmbeddingEngine()
question_embeddings = embedding_engine.get_embeddings(questions)
answer_embeddings = embedding_engine.get_embeddings(answers)

# Index vào Milvus
client = MilvusClient(collection_name="custom_collection")
client.index_data(
    Questions=questions,
    Answers=answers,
    Question_embeddings=question_embeddings,
    Answer_embeddings=answer_embeddings
)
```

## Testing và debugging

### 1. Test connection

```python
# test_connections.py
from data.milvus.milvus_client import MilvusClient
from data.cache.redis_cache import ShortTermMemory

# Test Milvus
try:
    client = MilvusClient()
    print("✓ Milvus connection successful")
except Exception as e:
    print(f"✗ Milvus connection failed: {e}")

# Test Redis
try:
    memory = ShortTermMemory()
    memory.store("test_key", "test_message")
    messages = memory.retrieve("test_key")
    print(f"✓ Redis connection successful: {messages}")
except Exception as e:
    print(f"✗ Redis connection failed: {e}")
```

### 2. Test search

```python
# test_search.py
from data.milvus.milvus_client import MilvusClient
from data.embeddings.embedding_engine import EmbeddingEngine

# Test search functionality
client = MilvusClient(collection_name="my_collection")
embedding_engine = EmbeddingEngine()

# Test query
query = "How to apply for scholarship?"
query_embedding = embedding_engine.get_query_embedding(query)

# Perform search
results = client.hybrid_search(
    query_text=query,
    query_dense_embedding=query_embedding,
    limit=3
)

print(f"Search results for '{query}':")
for i, result in enumerate(results):
    print(f"{i+1}. {result['Question']}")
    print(f"   Answer: {result['Answer']}")
    print(f"   Score: {result['score']}")
    print()
```

### 3. Test agent

```python
# test_agent.py
import asyncio
from llm.base import AgentClient
from utils.basetools import create_faq_tool

# Tạo agent
faq_tool = create_faq_tool(collection_name="my_collection")
agent = AgentClient(
    model=model,
    system_prompt="You are a test assistant.",
    tools=[faq_tool]
).create_agent()

# Test queries
test_queries = [
    "What is the admission process?",
    "How to apply for scholarship?",
    "What are the requirements?"
]

async def test_agent():
    for query in test_queries:
        print(f"\nQuery: {query}")
        response = await agent.run(query)
        print(f"Response: {response.output}")

# Chạy test
asyncio.run(test_agent())
```

## Customization nâng cao

### 1. Custom system prompt

```python
# custom_prompts.py
CUSTOMER_SERVICE_PROMPT = """
You are a customer service representative for a university.
Your role is to:
1. Answer questions about admissions, courses, and scholarships
2. Be helpful and professional
3. Use the FAQ tool to find accurate information
4. If you don't know something, admit it and offer to help find the answer
5. Always end with asking if there's anything else you can help with
"""

agent = AgentClient(
    model=model,
    system_prompt=CUSTOMER_SERVICE_PROMPT,
    tools=[faq_tool]
).create_agent()
```

### 2. Custom error handling

```python
# custom_error_handling.py
from handlers.error_handler import ErrorHandler

error_handler = ErrorHandler()

@cl.on_message
async def main(message: cl.Message):
    try:
        response = await agent.run(message.content)
        await cl.Message(content=str(response.output)).send()
    except Exception as e:
        error_message = error_handler.handle_exception(e)
        await cl.Message(content=error_message).send()
```

### 3. Custom UI với Chainlit

```python
# custom_ui.py
import chainlit as cl

@cl.on_chat_start
async def on_chat_start():
    await cl.Message(
        content="Welcome! I'm your AI assistant. How can I help you today?"
    ).send()

@cl.on_message
async def main(message: cl.Message):
    # Show thinking indicator
    async with cl.Step(name="Processing", type="run") as step:
        response = await agent.run(message.content)
        step.output = str(response.output)
    
    await cl.Message(content=str(response.output)).send()
```

## Deployment

### 1. Local deployment

```bash
# Chạy với uvicorn
uvicorn app:app --host 0.0.0.0 --port 8000

# Hoặc với chainlit
chainlit run app.py --host 0.0.0.0 --port 8000
```