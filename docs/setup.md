# Hướng dẫn cài đặt và cấu hình

## Yêu cầu hệ thống

### Phần mềm cần thiết
- **Python 3.12+** (bắt buộc)
- **Redis Server** (cho short-term memory)
- **Milvus Vector Database** (cho semantic search)

### Các dịch vụ cloud
- **Google Gemini API** (cho LLM)
- **OpenAI API** (cho embeddings)
- **Milvus Cloud** (tùy chọn, thay thế cho Milvus local)

## Cài đặt

### 1. Clone repository
```bash
git clone https://github.com/waanney/summerschool_workshop.git
cd summerschool_workshop
```

### 2. Tạo môi trường ảo
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# hoặc
venv\Scripts\activate     # Windows
```

### 3. Cài đặt dependencies
```bash
pip install .
```

### 4. Cài đặt Redis Server

#### Windows
```bash
# Sử dụng Chocolatey
choco install redis-64

# Hoặc sử dụng Windows Subsystem for Linux (WSL)
wsl --install Ubuntu
# Sau đó trong WSL:
sudo apt-get update
sudo apt-get install redis-server
```

#### MacOS
```bash
brew install redis
```

#### Linux
```bash
sudo apt-get update
sudo apt-get install redis-server
```

### 5. Cài đặt Milvus

#### Docker (Khuyến nghị)
```bash
# Tải và chạy Milvus Standalone
wget https://github.com/milvus-io/milvus/releases/download/v2.4.0/milvus-standalone-docker-compose.yml -O docker-compose.yml
docker-compose up -d
```

#### Milvus Cloud
1. Truy cập [Milvus Cloud](https://cloud.milvus.io/)
2. Tạo tài khoản và cluster
3. Lấy connection URI và token

## Cấu hình biến môi trường

### 1. Tạo file `.env`
```bash
cp .env.example .env
```

### 2. Cấu hình các biến môi trường
```env
# API Keys
GEMINI_API_KEY=your_gemini_api_key_here
OPENAI_API_KEY=your_openai_api_key_here

# Milvus Configuration
MILVUS_URI=http://localhost:19530
MILVUS_TOKEN=your_milvus_token_here

# Redis Configuration (mặc định)
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0

# Email Configuration (cho email tool)
SENDER_EMAIL=your_email@gmail.com
SENDER_PASSWORD=your_app_password

# API Configuration
API_HOST=127.0.0.1
API_PORT=7000
```

### 3. Lấy API Keys

#### Google Gemini API
1. Truy cập [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Tạo API key mới
3. Copy và paste vào file `.env`

#### OpenAI API
1. Truy cập [OpenAI Platform](https://platform.openai.com/api-keys)
2. Tạo API key mới
3. Copy và paste vào file `.env`

## Kiểm tra cài đặt

### 1. Kiểm tra Redis
```bash
redis-cli ping
# Kết quả: PONG
```

### 2. Kiểm tra Milvus
```bash
# Thử kết nối qua Python
python -c "from pymilvus import connections; connections.connect(host='localhost', port='19530'); print('Milvus connected successfully')"
```

### 3. Chạy test
```bash
# Test basic functionality
python test_sparse_search.py

# Test memory system
python -c "from src.data.cache.redis_cache import ShortTermMemory; sm = ShortTermMemory(); print('Memory system working')"
```

## Khắc phục sự cố

### Lỗi thường gặp

#### Redis connection refused
```bash
# Khởi động Redis server
redis-server
```

#### Milvus connection timeout
```bash
# Kiểm tra Docker containers
docker ps
docker-compose logs milvus-standalone
```

#### Import errors
```bash
# Cài đặt lại dependencies
pip install --force-reinstall .
```

#### Permission denied với Docker
```bash
# Thêm user vào Docker group (Linux)
sudo usermod -aG docker $USER
# Restart terminal
```

### Debugging

#### Bật debug mode
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

#### Kiểm tra logs
```bash
# Xem Redis logs
redis-cli monitor

# Xem Milvus logs
docker-compose logs -f milvus-standalone
```

## Cấu hình nâng cao

### 1. Tùy chỉnh Milvus
```python
# Trong config/system_config.py
self.MILVUS_URL = "your_custom_milvus_url"
self.MILVUS_TOKEN = "your_custom_token"
```

### 2. Tùy chỉnh Redis
```python
# Trong src/data/cache/redis_cache.py
def __init__(self, host="your_redis_host", port=6379, db=0, max_messages=15):
```

### 3. Tùy chỉnh model
```json
// Trong config/model_config.json
{
    "LLM": {
        "response_llm": {
            "model_id": "gemini-2.0-flash",
            "provider": "google-gla",
            "temperature": 0.7
        }
    }
}
```

## Bước tiếp theo

Sau khi cài đặt thành công, bạn có thể:
1. Đọc [Architecture Documentation](architecture.md)
2. Xem [Usage Examples](usage.md)
3. Tham khảo [API Reference](api.md)
4. Chạy demo đầu tiên với [Quick Start Guide](quickstart.md)
