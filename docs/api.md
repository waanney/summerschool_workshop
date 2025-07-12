# API Reference

## Core Components

### AgentClient

Wrapper class cho PydanticAI Agent với Google Gemini integration.

```python
class AgentClient:
    def __init__(self, model: GeminiModel, system_prompt: str, tools: List[Callable])
```

**Parameters:**
- `model`: GeminiModel instance
- `system_prompt`: System prompt cho agent
- `tools`: List các tools để agent sử dụng

**Methods:**
- `create_agent()`: Tạo và trả về PydanticAI Agent instance

**Example:**
```python
from llm.base import AgentClient
from pydantic_ai.models.gemini import GeminiModel
from pydantic_ai.providers.google_gla import GoogleGLAProvider

provider = GoogleGLAProvider(api_key="your_api_key")
model = GeminiModel('gemini-2.0-flash', provider=provider)

agent = AgentClient(
    model=model,
    system_prompt="You are a helpful assistant",
    tools=[faq_tool]
).create_agent()
```

---

## Data Layer

### MilvusClient

Client cho Milvus vector database với hybrid search capabilities.

```python
class MilvusClient:
    def __init__(self, collection_name: str = "summerschool_workshop")
```

**Parameters:**
- `collection_name`: Tên collection trong Milvus

**Methods:**

#### `index_data()`
```python
def index_data(
    self,
    Questions: List[str],
    Answers: List[str],
    Question_embeddings: List[List[float]],
    Answer_embeddings: List[List[float]],
    sparse_Question_embeddings: Optional[List[List[float]]] = None,
    sparse_Answer_embeddings: Optional[List[List[float]]] = None
)
```

Index dữ liệu vào Milvus collection.

**Parameters:**
- `Questions`: List câu hỏi
- `Answers`: List câu trả lời
- `Question_embeddings`: Dense embeddings cho câu hỏi
- `Answer_embeddings`: Dense embeddings cho câu trả lời
- `sparse_Question_embeddings`: Sparse embeddings cho câu hỏi (optional)
- `sparse_Answer_embeddings`: Sparse embeddings cho câu trả lời (optional)

#### `hybrid_search()`
```python
def hybrid_search(
    self,
    query_text: str,
    query_dense_embedding: List[float],
    limit: int = 5,
    search_answers: bool = False,
    ranker_weights: Optional[List[float]] = None
) -> List[Dict[str, Any]]
```

Thực hiện hybrid search kết hợp semantic và keyword search.

**Parameters:**
- `query_text`: Text query cho BM25 search
- `query_dense_embedding`: Dense embedding vector cho semantic search
- `limit`: Số lượng kết quả tối đa
- `search_answers`: Có search trong answers không
- `ranker_weights`: Weights cho reranking

**Returns:**
- List of dictionaries chứa search results

**Example:**
```python
client = MilvusClient(collection_name="my_faq")
embedding_engine = EmbeddingEngine()

query = "How to apply for scholarship?"
query_embedding = embedding_engine.get_query_embedding(query)

results = client.hybrid_search(
    query_text=query,
    query_dense_embedding=query_embedding,
    limit=5
)
```

---

### ShortTermMemory

Redis-based memory system cho conversation history.

```python
class ShortTermMemory:
    def __init__(self, host="localhost", port=6379, db=0, max_messages=15)
```

**Parameters:**
- `host`: Redis server host
- `port`: Redis server port
- `db`: Redis database number
- `max_messages`: Số lượng message tối đa lưu trữ

**Methods:**

#### `store()`
```python
def store(self, key: str, message: str)
```

Lưu message vào Redis.

#### `retrieve()`
```python
def retrieve(self, key: str) -> List[str]
```

Lấy tất cả messages cho session.

#### `get_history_context()`
```python
def get_history_context(self, session_key: str) -> str
```

Xây dựng conversation history context.

**Example:**
```python
memory = ShortTermMemory(max_messages=10)
session_key = "user_123"

memory.store_user_message(session_key, "Hello")
memory.store_bot_message(session_key, "Hi there!")

context = memory.get_history_context(session_key)
```

---

### EmbeddingEngine

Wrapper cho OpenAI embeddings API.

```python
class EmbeddingEngine:
    def __init__(self, model_name: str = "all-MiniLM-L6-v2", save_path: str = "embedding_state.json")
```

**Parameters:**
- `model_name`: Tên model embedding
- `save_path`: Path để save/load state

**Methods:**

#### `get_embeddings()`
```python
def get_embeddings(self, texts: List[str]) -> List[List[float]]
```

Generate embeddings cho list of texts.

#### `get_query_embedding()`
```python
def get_query_embedding(self, query: str) -> List[float]
```

Generate embedding cho single query.

**Example:**
```python
engine = EmbeddingEngine()
embeddings = engine.get_embeddings(["Hello world", "How are you?"])
query_embedding = engine.get_query_embedding("What is AI?")
```

---

## Tools

### FAQ Tool

Tool để search trong FAQ database.

```python
class SearchInput(BaseModel):
    query: str = Field(..., description="Search query")
    limit: int = Field(3, description="Number of results")
    search_answers: bool = Field(False, description="Search in answers")

class SearchOutput(BaseModel):
    results: List[Dict[str, Any]] = Field(..., description="Search results")
```

#### `create_faq_tool()`
```python
def create_faq_tool(collection_name: str = "summerschool_workshop") -> Callable
```

Tạo FAQ tool với pre-configured collection name.

**Example:**
```python
from utils.basetools import create_faq_tool

faq_tool = create_faq_tool(collection_name="my_collection")

# Sử dụng trong agent
agent = AgentClient(
    model=model,
    system_prompt="Use FAQ tool to answer questions",
    tools=[faq_tool]
).create_agent()
```

---

### HTTP Tool

Tool để thực hiện HTTP requests.

```python
class HttpRequest(BaseModel):
    url: str
    method: HTTPMethod = HTTPMethod.GET
    headers: Optional[Dict[str, str]] = None
    params: Optional[Dict[str, str]] = None
    body_type: BodyType = BodyType.JSON
    body: Optional[Union[Dict[str, Any], str, bytes]] = None
    response_type: ResponseType = ResponseType.JSON
    timeout: int = 10

class HttpResponse(BaseModel):
    status_code: int
    headers: Dict[str, str]
    body: Union[Dict[str, Any], str, bytes]
```

#### `http_tool()`
```python
def http_tool(req: HttpRequest) -> HttpResponse
```

**Example:**
```python
from utils.basetools import http_tool, HttpRequest, HTTPMethod

request = HttpRequest(
    url="https://api.example.com/data",
    method=HTTPMethod.GET,
    headers={"Authorization": "Bearer token"}
)

response = http_tool(request)
print(response.status_code)
```

---

### Email Tool

Tool để gửi email.

```python
class EmailToolInput(BaseModel):
    subject: str = Field(..., description="Email subject")
    body: str = Field(..., description="Email body")

class EmailToolOutput(BaseModel):
    success: bool = Field(..., description="Success status")
    message: str = Field(..., description="Result message")
```

#### `create_send_email_tool()`
```python
def create_send_email_tool(
    to_emails: List[str],
    sender_email: Optional[str] = None,
    sender_password: Optional[str] = None
) -> Callable
```

**Example:**
```python
from utils.basetools import create_send_email_tool, EmailToolInput

email_tool = create_send_email_tool(
    to_emails=["admin@example.com"],
    sender_email="bot@example.com",
    sender_password="app_password"
)

# Sử dụng
result = email_tool(EmailToolInput(
    subject="Test Subject",
    body="Test body"
))
```

---

### Calculator Tool

Tool để thực hiện tính toán.

```python
class CalculationInput(BaseModel):
    expression: str = Field(..., description="Mathematical expression")

class CalculationOutput(BaseModel):
    result: float = Field(..., description="Calculation result")
    expression: str = Field(..., description="Original expression")
```

#### `calculate()`
```python
def calculate(input: CalculationInput) -> CalculationOutput
```

**Example:**
```python
from utils.basetools import calculate, CalculationInput

result = calculate(CalculationInput(expression="2 + 3 * 4"))
print(result.result)  # 14.0
```

---

## Indexing

### MilvusIndexer

Utility để index dữ liệu từ CSV/Excel vào Milvus.

```python
class MilvusIndexer:
    def __init__(self, collection_name="summerschool_workshop", faq_file="data.csv")
```

**Parameters:**
- `collection_name`: Tên collection
- `faq_file`: Path đến file CSV/Excel

**Methods:**

#### `run()`
```python
def run()
```

Chạy quá trình indexing hoàn chỉnh.

**Example:**
```python
from data.milvus.indexing import MilvusIndexer

indexer = MilvusIndexer(
    collection_name="my_faq",
    faq_file="src/data/mock_data/faq.csv"
)
indexer.run()
```

---

## Memory Management

### MessageMemoryHandler

High-level interface cho memory management.

```python
class MessageMemoryHandler:
    def __init__(self, max_messages: int = 15)
```

**Methods:**

#### `get_history_message()`
```python
def get_history_message(self, message_content: str) -> str
```

Chuẩn bị message với context từ memory.

#### `store_bot_response()`
```python
def store_bot_response(self, response: str)
```

Lưu bot response vào memory.

**Example:**
```python
from data.cache.memory_handler import MessageMemoryHandler

memory_handler = MessageMemoryHandler(max_messages=10)

# Trong Chainlit handler
@cl.on_message
async def main(message: cl.Message):
    full_message = memory_handler.get_history_message(message.content)
    response = await agent.run(full_message)
    memory_handler.store_bot_response(str(response.output))
```

---

## Configuration

### Settings

System configuration class.

```python
class Settings:
    APP_NAME: str = "Chatbot API"
    DEBUG: bool = True
    MILVUS_URL: str = os.getenv("MILVUS_URI")
    MILVUS_TOKEN: str = os.getenv("MILVUS_TOKEN")
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY")
    RATE_LIMIT_PER_MINUTE: int = 60
```

**Usage:**
```python
from config.system_config import settings

print(settings.MILVUS_URL)
print(settings.RATE_LIMIT_PER_MINUTE)
```

---

## Error Handling

### ErrorHandler

Centralized error handling.

```python
class ErrorHandler:
    def __init__(self, log_file="app.log")
    
    def handle_exception(self, exception: Exception) -> str
```

**Example:**
```python
from handlers.error_handler import ErrorHandler

error_handler = ErrorHandler()

try:
    # Some operation
    pass
except Exception as e:
    error_message = error_handler.handle_exception(e)
    print(error_message)
```

---

## Logging

### Logger Setup

```python
def setup_logger(log_file="app.log") -> logging.Logger
```

**Example:**
```python
from utils.logger import setup_logger

logger = setup_logger("my_app.log")
logger.info("Application started")
logger.error("An error occurred")
```

---

## Environment Variables

### Required Variables

```env
# API Keys
GEMINI_API_KEY=your_gemini_api_key
OPENAI_API_KEY=your_openai_api_key

# Database
MILVUS_URI=http://localhost:19530
MILVUS_TOKEN=your_milvus_token

# Redis (optional, defaults to localhost)
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0

# Email (optional)
SENDER_EMAIL=your_email@gmail.com
SENDER_PASSWORD=your_app_password
```

---

## Common Patterns

### 1. Basic Agent Setup

```python
from llm.base import AgentClient
from utils.basetools import create_faq_tool
from pydantic_ai.models.gemini import GeminiModel
from pydantic_ai.providers.google_gla import GoogleGLAProvider
import os

# Setup model
provider = GoogleGLAProvider(api_key=os.getenv("GEMINI_API_KEY"))
model = GeminiModel('gemini-2.0-flash', provider=provider)

# Create tools
faq_tool = create_faq_tool(collection_name="my_collection")

# Create agent
agent = AgentClient(
    model=model,
    system_prompt="You are a helpful assistant",
    tools=[faq_tool]
).create_agent()
```

### 2. Chainlit Integration

```python
import chainlit as cl

@cl.on_message
async def main(message: cl.Message):
    response = await agent.run(message.content)
    await cl.Message(content=str(response.output)).send()
```

### 3. Memory Integration

```python
from data.cache.memory_handler import MessageMemoryHandler

memory_handler = MessageMemoryHandler(max_messages=15)

@cl.on_message
async def main(message: cl.Message):
    full_message = memory_handler.get_history_message(message.content)
    response = await agent.run(full_message)
    memory_handler.store_bot_response(str(response.output))
    await cl.Message(content=str(response.output)).send()
```

### 4. Data Indexing

```python
from data.milvus.indexing import MilvusIndexer

indexer = MilvusIndexer(
    collection_name="my_collection",
    faq_file="data/my_faq.csv"
)
indexer.run()
```

Đây là API reference hoàn chỉnh cho tất cả các components chính trong hệ thống. Sử dụng các examples để hiểu cách integrate các components với nhau.
