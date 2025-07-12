# Troubleshooting và FAQ

## Các lỗi thường gặp

### 1. Connection Errors

#### Lỗi: "Connection refused to Milvus"
**Nguyên nhân**: Milvus server chưa được khởi động hoặc cấu hình sai.

**Giải pháp**:
```bash
# Kiểm tra Milvus service
docker ps | grep milvus

# Khởi động Milvus
docker-compose up -d milvus

# Kiểm tra logs
docker-compose logs milvus

# Test connection
python -c "from pymilvus import connections; connections.connect(host='localhost', port='19530'); print('Connected')"
```

#### Lỗi: "Redis connection failed"
**Nguyên nhân**: Redis server không chạy hoặc cấu hình sai.

**Giải pháp**:
```bash
# Kiểm tra Redis
redis-cli ping

# Khởi động Redis
redis-server

# Hoặc với Docker
docker run -d -p 6379:6379 redis:7-alpine

# Test connection
python -c "import redis; r = redis.Redis(); r.ping(); print('Connected')"
```

---

### 2. Authentication Errors

#### Lỗi: "Invalid API key for Gemini"
**Nguyên nhân**: API key không hợp lệ hoặc chưa được cấu hình.

**Giải pháp**:
```bash
# Kiểm tra API key
echo $GEMINI_API_KEY

# Tạo API key mới tại Google AI Studio
# https://makersuite.google.com/app/apikey

# Cập nhật .env file
GEMINI_API_KEY=your_new_api_key_here
```

#### Lỗi: "OpenAI API key invalid"
**Nguyên nhân**: OpenAI API key không đúng định dạng hoặc hết hạn.

**Giải pháp**:
```bash
# Kiểm tra format API key (phải bắt đầu bằng sk-)
echo $OPENAI_API_KEY

# Test API key
curl -H "Authorization: Bearer $OPENAI_API_KEY" https://api.openai.com/v1/models

# Tạo API key mới tại OpenAI Platform
# https://platform.openai.com/api-keys
```

---

### 3. Import và Module Errors

#### Lỗi: "ModuleNotFoundError: No module named 'pydantic_ai'"
**Nguyên nhân**: Dependencies chưa được cài đặt đúng.

**Giải pháp**:
```bash
# Cài đặt lại dependencies
pip install --force-reinstall .

# Hoặc cài đặt từ requirements.txt
pip install -r requirements.txt

# Kiểm tra installation
pip list | grep pydantic-ai
```

#### Lỗi: "ImportError: cannot import name 'Collection' from 'pymilvus'"
**Nguyên nhân**: Pymilvus version không tương thích.

**Giải pháp**:
```bash
# Kiểm tra version
pip show pymilvus

# Cài đặt version tương thích
pip install pymilvus==2.5.8

# Hoặc upgrade
pip install --upgrade pymilvus
```

---

### 4. Data và Indexing Errors

#### Lỗi: "Collection not found"
**Nguyên nhân**: Collection chưa được tạo hoặc tên không đúng.

**Giải pháp**:
```python
# Kiểm tra collections có sẵn
from pymilvus import utility
print(utility.list_collections())

# Tạo collection mới
from data.milvus.indexing import MilvusIndexer
indexer = MilvusIndexer(
    collection_name="your_collection",
    faq_file="your_data.csv"
)
indexer.run()
```

#### Lỗi: "Embedding dimension mismatch"
**Nguyên nhân**: Dimension của embeddings không khớp với schema.

**Giải pháp**:
```python
# Kiểm tra dimension của embeddings
from data.embeddings.embedding_engine import EmbeddingEngine
engine = EmbeddingEngine()
embedding = engine.get_query_embedding("test")
print(f"Embedding dimension: {len(embedding)}")

# Cập nhật schema nếu cần
# Dimension mặc định: 384 (sentence-transformers)
# OpenAI text-embedding-3-small: 1536
```

---

### 5. Memory và Performance Issues

#### Lỗi: "Out of memory during indexing"
**Nguyên nhân**: Dữ liệu quá lớn hoặc RAM không đủ.

**Giải pháp**:
```python
# Xử lý dữ liệu theo batch
def batch_process_data(data, batch_size=1000):
    for i in range(0, len(data), batch_size):
        batch = data[i:i+batch_size]
        # Process batch
        process_batch(batch)
        
        # Clear memory
        import gc
        gc.collect()

# Giảm batch size
batch_size = 500  # Thay vì 1000
```

#### Lỗi: "Redis memory limit exceeded"
**Nguyên nhân**: Redis memory không đủ cho session data.

**Giải pháp**:
```python
# Giảm max_messages
memory_handler = MessageMemoryHandler(max_messages=5)  # Thay vì 15

# Hoặc cấu hình Redis memory
# redis.conf
maxmemory 256mb
maxmemory-policy allkeys-lru
```

---

### 6. Chainlit và UI Errors

#### Lỗi: "Chainlit app not starting"
**Nguyên nhân**: Port đã được sử dụng hoặc cấu hình sai.

**Giải pháp**:
```bash
# Kiểm tra port
lsof -i :8000

# Chạy trên port khác
chainlit run app.py --port 8001

# Hoặc kill process đang dùng port
kill -9 <PID>
```

#### Lỗi: "Session not found"
**Nguyên nhân**: Session management không đúng.

**Giải pháp**:
```python
# Kiểm tra session setup
import chainlit as cl

@cl.on_chat_start
async def on_chat_start():
    cl.user_session.set("initialized", True)
    print("Session initialized")

@cl.on_message
async def main(message: cl.Message):
    if not cl.user_session.get("initialized"):
        await cl.Message(content="Please refresh the page").send()
        return
    # Handle message
```

---

## Debugging Tips

### 1. Enable Debug Logging

```python
# Enable debug mode
import logging
logging.basicConfig(level=logging.DEBUG)

# For specific modules
logging.getLogger('pymilvus').setLevel(logging.DEBUG)
logging.getLogger('redis').setLevel(logging.DEBUG)
```

### 2. Component Testing

```python
# Test individual components
def test_milvus_connection():
    try:
        from data.milvus.milvus_client import MilvusClient
        client = MilvusClient()
        print("✓ Milvus connection successful")
    except Exception as e:
        print(f"✗ Milvus connection failed: {e}")

def test_redis_connection():
    try:
        from data.cache.redis_cache import ShortTermMemory
        memory = ShortTermMemory()
        memory.store("test", "message")
        print("✓ Redis connection successful")
    except Exception as e:
        print(f"✗ Redis connection failed: {e}")

def test_embedding_engine():
    try:
        from data.embeddings.embedding_engine import EmbeddingEngine
        engine = EmbeddingEngine()
        embedding = engine.get_query_embedding("test")
        print(f"✓ Embedding engine working, dimension: {len(embedding)}")
    except Exception as e:
        print(f"✗ Embedding engine failed: {e}")

# Run tests
test_milvus_connection()
test_redis_connection()
test_embedding_engine()
```

### 3. Performance Profiling

```python
import time
import psutil
from functools import wraps

def profile_function(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        process = psutil.Process()
        memory_before = process.memory_info().rss / 1024 / 1024
        
        result = func(*args, **kwargs)
        
        end_time = time.time()
        memory_after = process.memory_info().rss / 1024 / 1024
        
        print(f"Function: {func.__name__}")
        print(f"Time: {end_time - start_time:.2f}s")
        print(f"Memory: {memory_after - memory_before:.2f}MB")
        
        return result
    return wrapper

@profile_function
def your_function():
    # Your code here
    pass
```

---

## FAQ

### Q1: Làm sao để thay đổi model AI?

**A**: Cập nhật trong `config/model_config.json`:
```json
{
    "LLM": {
        "response_llm": {
            "model_id": "gemini-2.0-flash-exp",
            "provider": "google-gla"
        }
    }
}
```

### Q2: Có thể sử dụng OpenAI GPT thay vì Gemini không?

**A**: Có, cần cập nhật code:
```python
from pydantic_ai.models.openai import OpenAIModel

model = OpenAIModel('gpt-4o', api_key=os.getenv('OPENAI_API_KEY'))
```

### Q3: Làm sao để tăng số lượng kết quả tìm kiếm?

**A**: Thay đổi limit trong search:
```python
results = client.hybrid_search(
    query_text=query,
    query_dense_embedding=embedding,
    limit=10  # Tăng từ 5 lên 10
)
```

### Q4: Làm sao để index dữ liệu từ database?

**A**: Tạo custom data loader:
```python
import sqlite3
from data.milvus.indexing import MilvusIndexer

class DatabaseIndexer(MilvusIndexer):
    def __init__(self, collection_name, db_path, query):
        self.db_path = db_path
        self.query = query
        super().__init__(collection_name, faq_file=None)
    
    def load_data(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(self.query)
        return cursor.fetchall()
```

### Q5: Làm sao để tạo custom tool?

**A**: Tham khảo pattern trong `src/utils/basetools/`:
```python
from pydantic import BaseModel, Field

class MyToolInput(BaseModel):
    param: str = Field(..., description="Parameter description")

class MyToolOutput(BaseModel):
    result: str = Field(..., description="Result description")

def my_tool(input: MyToolInput) -> MyToolOutput:
    # Tool logic
    return MyToolOutput(result="processed")
```

### Q6: Làm sao để backup dữ liệu?

**A**: Backup collections và Redis:
```bash
# Backup Milvus collections
python -c "
from pymilvus import utility
collections = utility.list_collections()
for col in collections:
    print(f'Backing up {col}')
    # Implement backup logic
"

# Backup Redis
redis-cli --rdb dump.rdb

# Backup với Docker
docker exec redis redis-cli BGSAVE
```

### Q7: Làm sao để scale hệ thống?

**A**: Các options:
1. **Horizontal scaling**: Sử dụng load balancer
2. **Milvus cluster**: Setup Milvus cluster mode
3. **Redis cluster**: Setup Redis cluster
4. **Async processing**: Sử dụng message queue

### Q8: Làm sao để monitor hệ thống?

**A**: Sử dụng monitoring tools:
```python
# Prometheus metrics
from prometheus_client import Counter, Histogram, generate_latest

request_count = Counter('requests_total', 'Total requests')
response_time = Histogram('response_time_seconds', 'Response time')

# Custom monitoring
class Monitor:
    def __init__(self):
        self.metrics = {}
    
    def track(self, metric_name, value):
        if metric_name not in self.metrics:
            self.metrics[metric_name] = []
        self.metrics[metric_name].append(value)
```

### Q9: Làm sao để handle rate limiting?

**A**: Implement rate limiting:
```python
import time
from collections import defaultdict

class RateLimiter:
    def __init__(self, max_requests=60, time_window=60):
        self.max_requests = max_requests
        self.time_window = time_window
        self.requests = defaultdict(list)
    
    def is_allowed(self, user_id):
        now = time.time()
        user_requests = self.requests[user_id]
        
        # Remove old requests
        user_requests[:] = [req for req in user_requests if now - req < self.time_window]
        
        if len(user_requests) >= self.max_requests:
            return False
        
        user_requests.append(now)
        return True
```

### Q10: Làm sao để test hệ thống?

**A**: Sử dụng pytest:
```python
import pytest
from your_app import agent

@pytest.fixture
def test_agent():
    return agent

def test_faq_query(test_agent):
    response = test_agent.run("What is AI?")
    assert response.output is not None
    assert len(response.output) > 0

def test_tool_integration():
    from utils.basetools import create_faq_tool
    tool = create_faq_tool("test_collection")
    # Test tool functionality
```

---

## Liên hệ Support

Nếu bạn gặp vấn đề không được giải quyết trong tài liệu này:

1. **Check logs**: Kiểm tra logs trong folder `logs/`
2. **GitHub Issues**: Tạo issue mới trên GitHub repository
3. **Documentation**: Đọc thêm documentation của các thư viện:
   - [PydanticAI](https://ai.pydantic.dev/)
   - [Milvus](https://milvus.io/docs)
   - [Chainlit](https://docs.chainlit.io/)
4. **Community**: Tham gia community discussion

**Debug checklist**:
- [ ] Environment variables đã được cấu hình
- [ ] All services (Milvus, Redis) đang chạy
- [ ] API keys có hiệu lực
- [ ] Dependencies đã được cài đặt
- [ ] Firewall không block connections
- [ ] Disk space đủ cho data và logs
