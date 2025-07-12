# Kiến trúc hệ thống

## Tổng quan

Summerschool Workshop là một hệ thống AI Agent tích hợp nhiều công nghệ tiên tiến:

- **Vector Database**: Milvus cho semantic search
- **Memory System**: Redis cho short-term memory
- **LLM**: Google Gemini 2.0 Flash
- **Embeddings**: OpenAI text-embedding-3-small
- **Framework**: PydanticAI cho agent orchestration
- **UI**: Chainlit cho conversational interface

## Kiến trúc tổng thể

```
┌─────────────────────────────────────────────────────────────────┐
│                        User Interface                           │
│                      (Chainlit Web UI)                         │
└─────────────────────────┬───────────────────────────────────────┘
                          │
┌─────────────────────────▼───────────────────────────────────────┐
│                    Agent Layer                                  │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐ │
│  │  AgentClient    │  │  PydanticAI     │  │  Tool System    │ │
│  │  (LLM Wrapper)  │  │  (Orchestrator) │  │  (FAQ, HTTP,    │ │
│  │                 │  │                 │  │   Email, etc.)  │ │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘ │
└─────────────────────────┬───────────────────────────────────────┘
                          │
┌─────────────────────────▼───────────────────────────────────────┐
│                    Data Layer                                   │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐ │
│  │  Milvus Vector  │  │  Redis Memory   │  │  Embedding      │ │
│  │  Database       │  │  Cache          │  │  Engine         │ │
│  │  (Semantic      │  │  (Short-term    │  │  (OpenAI)       │ │
│  │   Search)       │  │   Memory)       │  │                 │ │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘ │
└─────────────────────────┬───────────────────────────────────────┘
                          │
┌─────────────────────────▼───────────────────────────────────────┐
│                External Services                                │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐ │
│  │  Google Gemini  │  │  OpenAI API     │  │  SMTP Server    │ │
│  │  API            │  │  (Embeddings)   │  │  (Email)        │ │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

## Các thành phần chính

### 1. Agent Layer

#### AgentClient (`src/llm/base.py`)
- Wrapper cho PydanticAI Agent
- Quản lý system prompt và tools
- Tích hợp với Google Gemini model

```python
class AgentClient:
    def __init__(self, system_prompt: str, tools: List[Callable], model: GeminiModel):
        self.model = model
        self.system_prompt = system_prompt
        self.tools = tools
```

#### Tool System (`src/utils/basetools/`)
- **FAQ Tool**: Tìm kiếm trong vector database
- **HTTP Tool**: Gọi API bên ngoài
- **Email Tool**: Gửi email thông báo
- **Calculator Tool**: Tính toán số học
- **File Tools**: Đọc và xử lý file

### 2. Data Layer

#### Milvus Vector Database (`src/data/milvus/`)
- **Hybrid Search**: Kết hợp dense và sparse vectors
- **BM25 Integration**: Full-text search với sparse vectors
- **Dynamic Schema**: Tự động tạo schema từ dữ liệu

```python
class MilvusClient:
    def hybrid_search(self, query_text: str, query_dense_embedding: List[float]) -> List[Dict]:
        # Combines semantic search (dense) with keyword search (sparse)
        pass
```

#### Redis Memory System (`src/data/cache/`)
- **Short-term Memory**: Lưu trữ conversation history
- **Session Management**: Quản lý user sessions
- **Message Limiting**: Giới hạn số lượng tin nhắn

```python
class ShortTermMemory:
    def __init__(self, max_messages=15):
        self.redis_client = redis.StrictRedis()
        self.max_messages = max_messages
```

#### Embedding Engine (`src/data/embeddings/`)
- **OpenAI Integration**: Sử dụng text-embedding-3-small
- **Batch Processing**: Xử lý nhiều text cùng lúc
- **Error Handling**: Xử lý lỗi gracefully

### 3. Data Processing Pipeline

```
Input Text → Embedding Engine → Vector Database → Search Results
     ↓              ↓                 ↓              ↓
User Query → Dense Embedding → Milvus Hybrid → Ranked Results
     ↓              ↓              Search         ↓
BM25 Tokens → Sparse Embedding →     ↓         → Agent Response
```

## Luồng dữ liệu chi tiết

### 1. Indexing Pipeline

```python
# 1. Load FAQ data
faq_data = load_faq_from_csv("data.csv")

# 2. Generate embeddings
dense_embeddings = embedding_engine.get_embeddings(questions)

# 3. Create collection with BM25 functions
collection = create_milvus_collection_with_bm25()

# 4. Index data
milvus_client.index_data(
    questions=questions,
    answers=answers,
    dense_embeddings=dense_embeddings
)
```

### 2. Search Pipeline

```python
# 1. User query comes in
user_query = "How to apply for scholarship?"

# 2. Generate query embedding
query_embedding = embedding_engine.get_query_embedding(user_query)

# 3. Perform hybrid search
results = milvus_client.hybrid_search(
    query_text=user_query,
    query_dense_embedding=query_embedding,
    limit=5
)

# 4. Return ranked results
return results
```

### 3. Memory Pipeline

```python
# 1. Store user message
memory_handler.store_user_message(session_id, user_query)

# 2. Get conversation context
context = memory_handler.get_history_context(session_id)

# 3. Build full prompt
full_prompt = f"{context}\nCURRENT QUESTION: {user_query}"

# 4. Store bot response
memory_handler.store_bot_response(session_id, response)
```

## Cấu hình và customization

### 1. Model Configuration (`config/model_config.json`)
```json
{
    "LLM": {
        "response_llm": {
            "model_id": "gemini-2.0-flash",
            "provider": "google-gla"
        }
    },
    "Embedding": {
        "model_id": "text-embedding-3-small",
        "provider": "openai"
    }
}
```

### 2. System Configuration (`config/system_config.py`)
```python
class Settings:
    MILVUS_URL = os.getenv("MILVUS_URI")
    MILVUS_TOKEN = os.getenv("MILVUS_TOKEN")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    RATE_LIMIT_PER_MINUTE = 60
```

## Scalability và Performance

### 1. Vector Database Optimization
- **Index Type**: IVF_FLAT cho balance giữa speed và accuracy
- **Metric Type**: L2 distance cho semantic similarity
- **Batch Size**: Tối ưu cho memory usage

### 2. Memory Management
- **Redis TTL**: Auto-expire old sessions
- **Message Limiting**: Giới hạn conversation history
- **Connection Pooling**: Reuse connections

### 3. API Rate Limiting
- **Gemini API**: 60 requests/minute
- **OpenAI API**: Depends on tier
- **Exponential Backoff**: Retry with delay

## Security Considerations

### 1. API Keys
- Store trong environment variables
- Never commit to version control
- Use different keys for different environments

### 2. Data Privacy
- Redis data encryption at rest
- Milvus access control
- Log sanitization

### 3. Network Security
- Use HTTPS for all external calls
- Validate all inputs
- Rate limiting và DDoS protection

## Monitoring và Logging

### 1. Application Logs
```python
# Setup logger
logger = setup_logger("app.log")
logger.info("Agent started")
logger.error("Connection failed", exc_info=True)
```

### 2. Performance Metrics
- Response time tracking
- Database query performance
- Memory usage monitoring

### 3. Error Handling
```python
class ErrorHandler:
    def handle_exception(self, exception: Exception):
        self.logger.error(f"{type(exception).__name__}: {str(exception)}")
        return "An error occurred. Please try again."
```

## Extensibility

### 1. Adding New Tools
```python
# Create new tool
def my_custom_tool(input: MyInput) -> MyOutput:
    # Tool logic here
    return MyOutput(result="success")

# Register with agent
agent = AgentClient(
    system_prompt="...",
    tools=[faq_tool, my_custom_tool]
)
```

### 2. Custom Models
```python
# Add new model provider
from pydantic_ai.models.custom import CustomModel
model = CustomModel("custom-model-name")
```

### 3. Data Sources
```python
# Add new data source
class CustomDataLoader:
    def load_data(self) -> List[Dict]:
        # Load from custom source
        pass
```

Kiến trúc này được thiết kế để dễ dàng mở rộng và customize theo nhu cầu cụ thể của từng dự án.
