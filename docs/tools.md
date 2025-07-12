# Tools và Extensions

## Tổng quan

Hệ thống cung cấp một bộ tools phong phú để mở rộng khả năng của AI agents. Các tools này được thiết kế theo pattern có thể tái sử dụng và dễ dàng tích hợp.

## Built-in Tools

### 1. FAQ Tool

Tool mạnh mẽ nhất để search trong knowledge base sử dụng hybrid search.

```python
from utils.basetools import create_faq_tool, SearchInput

# Tạo tool
faq_tool = create_faq_tool(collection_name="my_knowledge_base")

# Sử dụng programmatically
result = faq_tool(SearchInput(
    query="How to apply for scholarship?",
    limit=5,
    search_answers=False
))

print(result.results)
```

**Features:**
- Hybrid search (semantic + keyword)
- Configurable collection name
- Adjustable result limit
- Option to search in answers

**Use cases:**
- Customer support chatbots
- Educational Q&A systems
- Internal knowledge management
- Documentation search

---

### 2. HTTP Tool

Versatile HTTP client cho việc gọi external APIs.

```python
from utils.basetools import http_tool, HttpRequest, HTTPMethod

# GET request
response = http_tool(HttpRequest(
    url="https://api.github.com/users/octocat",
    method=HTTPMethod.GET
))

# POST request with JSON
response = http_tool(HttpRequest(
    url="https://api.example.com/data",
    method=HTTPMethod.POST,
    headers={"Content-Type": "application/json"},
    body={"name": "John", "email": "john@example.com"}
))

# POST request with form data
response = http_tool(HttpRequest(
    url="https://api.example.com/form",
    method=HTTPMethod.POST,
    body_type=BodyType.FORM,
    body={"field1": "value1", "field2": "value2"}
))
```

**Features:**
- Support tất cả HTTP methods
- Flexible body types (JSON, Form, Raw)
- Custom headers và parameters
- Configurable timeout
- Multiple response types

**Use cases:**
- API integration
- Web scraping
- Data fetching
- Third-party service calls

---

### 3. Email Tool

Professional email sending capabilities.

```python
from utils.basetools import create_send_email_tool, EmailToolInput

# Tạo email tool
email_tool = create_send_email_tool(
    to_emails=["admin@company.com", "support@company.com"],
    sender_email="bot@company.com",
    sender_password="app_password"
)

# Gửi email
result = email_tool(EmailToolInput(
    subject="New Support Request",
    body="A new support request has been received from user John Doe."
))

print(result.success)  # True/False
print(result.message)  # Success/Error message
```

**Features:**
- Multiple recipients
- HTML/Plain text support
- SMTP configuration
- Error handling
- Environment variable support

**Use cases:**
- Notifications
- Alerts
- Reports
- Customer communication

---

### 4. Calculator Tool

Advanced mathematical calculations.

```python
from utils.basetools import calculate, CalculationInput

# Basic calculations
result = calculate(CalculationInput(expression="2 + 3 * 4"))
print(result.result)  # 14.0

# Complex expressions
result = calculate(CalculationInput(expression="sqrt(16) + log(100)"))
print(result.result)  # 6.0

# Trigonometric functions
result = calculate(CalculationInput(expression="sin(pi/2) + cos(0)"))
print(result.result)  # 2.0
```

**Features:**
- Basic arithmetic operations
- Trigonometric functions
- Logarithmic functions
- Scientific constants
- Memory operations

**Use cases:**
- Financial calculations
- Scientific computations
- Data analysis
- Engineering calculations

---

### 5. File Tools

Comprehensive file operations.

```python
from utils.basetools import create_read_file_tool, FileContentOutput

# Tạo file reader tool
file_tool = create_read_file_tool(allowed_extensions=[".txt", ".md", ".json"])

# Đọc file
content = file_tool("path/to/file.txt")
print(content.content)

# Search trong file
from utils.basetools import create_search_in_file_tool

search_tool = create_search_in_file_tool(
    file_path="large_document.txt",
    search_type="fuzzy"
)

results = search_tool(SearchInput(
    query="important information",
    limit=5
))
```

**Features:**
- Multiple file format support
- Content extraction
- Search within files
- Fuzzy matching
- Security restrictions

**Use cases:**
- Document analysis
- Content extraction
- Data processing
- Information retrieval

---

## Creating Custom Tools

### 1. Basic Tool Structure

```python
from pydantic import BaseModel, Field
from typing import Optional

class MyToolInput(BaseModel):
    parameter1: str = Field(..., description="Description of parameter1")
    parameter2: int = Field(default=10, description="Description of parameter2")
    optional_param: Optional[str] = Field(None, description="Optional parameter")

class MyToolOutput(BaseModel):
    result: str = Field(..., description="Tool execution result")
    metadata: dict = Field(default_factory=dict, description="Additional metadata")

def my_custom_tool(input: MyToolInput) -> MyToolOutput:
    """
    Custom tool description for the AI agent.
    
    Args:
        input: Tool input parameters
        
    Returns:
        Tool execution result
    """
    # Tool logic here
    result = f"Processed {input.parameter1} with value {input.parameter2}"
    
    return MyToolOutput(
        result=result,
        metadata={"processed_at": "2024-01-01T00:00:00Z"}
    )
```

### 2. Database Tool Example

```python
import sqlite3
from typing import List, Dict, Any

class DatabaseQuery(BaseModel):
    query: str = Field(..., description="SQL query to execute")
    parameters: Optional[List[Any]] = Field(None, description="Query parameters")

class DatabaseResult(BaseModel):
    rows: List[Dict[str, Any]] = Field(..., description="Query results")
    count: int = Field(..., description="Number of rows returned")

def database_tool(input: DatabaseQuery) -> DatabaseResult:
    """Execute SQL queries on the database."""
    
    # Connect to database
    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row  # Return dict-like rows
    
    try:
        cursor = conn.cursor()
        if input.parameters:
            cursor.execute(input.query, input.parameters)
        else:
            cursor.execute(input.query)
        
        rows = [dict(row) for row in cursor.fetchall()]
        
        return DatabaseResult(
            rows=rows,
            count=len(rows)
        )
    
    finally:
        conn.close()
```

### 3. Web Scraping Tool

```python
import requests
from bs4 import BeautifulSoup
from typing import List

class WebScrapingInput(BaseModel):
    url: str = Field(..., description="URL to scrape")
    selector: str = Field(..., description="CSS selector for elements")
    limit: int = Field(10, description="Maximum number of elements")

class WebScrapingOutput(BaseModel):
    elements: List[str] = Field(..., description="Scraped elements")
    url: str = Field(..., description="Source URL")

def web_scraping_tool(input: WebScrapingInput) -> WebScrapingOutput:
    """Scrape content from web pages."""
    
    # Fetch webpage
    response = requests.get(input.url)
    response.raise_for_status()
    
    # Parse HTML
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Extract elements
    elements = soup.select(input.selector)
    texts = [elem.get_text(strip=True) for elem in elements[:input.limit]]
    
    return WebScrapingOutput(
        elements=texts,
        url=input.url
    )
```

### 4. External API Integration Tool

```python
import requests
from typing import Dict, Any

class WeatherInput(BaseModel):
    city: str = Field(..., description="City name")
    country: str = Field("VN", description="Country code")
    units: str = Field("metric", description="Temperature units")

class WeatherOutput(BaseModel):
    temperature: float = Field(..., description="Current temperature")
    description: str = Field(..., description="Weather description")
    humidity: int = Field(..., description="Humidity percentage")
    city: str = Field(..., description="City name")

def weather_tool(input: WeatherInput) -> WeatherOutput:
    """Get current weather information."""
    
    # API call (example with OpenWeatherMap)
    api_key = os.getenv("OPENWEATHER_API_KEY")
    url = f"https://api.openweathermap.org/data/2.5/weather"
    
    params = {
        "q": f"{input.city},{input.country}",
        "appid": api_key,
        "units": input.units
    }
    
    response = requests.get(url, params=params)
    response.raise_for_status()
    
    data = response.json()
    
    return WeatherOutput(
        temperature=data["main"]["temp"],
        description=data["weather"][0]["description"],
        humidity=data["main"]["humidity"],
        city=data["name"]
    )
```

## Tool Configuration và Best Practices

### 1. Tool Factory Pattern

```python
def create_database_tool(database_path: str, read_only: bool = True):
    """Factory function to create database tools with specific configurations."""
    
    def configured_database_tool(input: DatabaseQuery) -> DatabaseResult:
        if read_only and input.query.strip().upper().startswith(('INSERT', 'UPDATE', 'DELETE')):
            raise ValueError("Write operations not allowed in read-only mode")
        
        # Use the configured database_path
        conn = sqlite3.connect(database_path)
        # ... rest of the implementation
        
    return configured_database_tool
```

### 2. Error Handling

```python
def safe_tool_wrapper(tool_func):
    """Decorator to add error handling to tools."""
    
    def wrapper(input_data):
        try:
            return tool_func(input_data)
        except Exception as e:
            # Log error
            logging.error(f"Tool error: {str(e)}")
            
            # Return error response
            return {
                "error": True,
                "message": f"Tool execution failed: {str(e)}",
                "input": input_data.dict() if hasattr(input_data, 'dict') else str(input_data)
            }
    
    return wrapper

@safe_tool_wrapper
def my_tool(input: MyToolInput) -> MyToolOutput:
    # Tool implementation
    pass
```

### 3. Caching Tools

```python
import functools
import hashlib
import json

def cache_tool_results(expiry_seconds: int = 3600):
    """Decorator to cache tool results."""
    
    def decorator(func):
        cache = {}
        
        @functools.wraps(func)
        def wrapper(input_data):
            # Create cache key
            cache_key = hashlib.md5(
                json.dumps(input_data.dict(), sort_keys=True).encode()
            ).hexdigest()
            
            # Check cache
            if cache_key in cache:
                result, timestamp = cache[cache_key]
                if time.time() - timestamp < expiry_seconds:
                    return result
            
            # Execute tool
            result = func(input_data)
            
            # Cache result
            cache[cache_key] = (result, time.time())
            
            return result
        
        return wrapper
    return decorator

@cache_tool_results(expiry_seconds=1800)  # Cache for 30 minutes
def expensive_api_tool(input: APIInput) -> APIOutput:
    # Expensive API call
    pass
```

## Tool Integration với Agents

### 1. Multi-tool Agent

```python
from llm.base import AgentClient
from utils.basetools import create_faq_tool, http_tool, create_send_email_tool

# Create multiple tools
faq_tool = create_faq_tool(collection_name="knowledge_base")
email_tool = create_send_email_tool(to_emails=["admin@company.com"])
weather_tool = weather_tool  # Custom tool from above

# Create agent with multiple tools
agent = AgentClient(
    model=model,
    system_prompt="""
    You are a comprehensive assistant with access to multiple tools:
    
    1. faq_tool - Search company knowledge base
    2. http_tool - Make HTTP requests to external APIs
    3. email_tool - Send notifications via email
    4. weather_tool - Get weather information
    
    Use the appropriate tool based on the user's request.
    """,
    tools=[faq_tool, http_tool, email_tool, weather_tool]
).create_agent()
```

### 2. Conditional Tool Usage

```python
def smart_agent_handler(user_message: str):
    """Intelligent tool selection based on user message."""
    
    # Simple keyword-based routing
    if "weather" in user_message.lower():
        tools = [weather_tool]
        prompt = "You are a weather assistant. Use weather_tool to get weather information."
    
    elif "faq" in user_message.lower() or "help" in user_message.lower():
        tools = [faq_tool]
        prompt = "You are a help assistant. Use faq_tool to search for information."
    
    else:
        tools = [faq_tool, weather_tool, http_tool]
        prompt = "You are a general assistant. Choose the appropriate tool based on the user's request."
    
    # Create agent with selected tools
    agent = AgentClient(
        model=model,
        system_prompt=prompt,
        tools=tools
    ).create_agent()
    
    return agent
```

## Testing Tools

### 1. Unit Testing

```python
import unittest
from utils.basetools import calculate, CalculationInput

class TestCalculatorTool(unittest.TestCase):
    
    def test_basic_addition(self):
        result = calculate(CalculationInput(expression="2 + 3"))
        self.assertEqual(result.result, 5.0)
    
    def test_complex_expression(self):
        result = calculate(CalculationInput(expression="2 * 3 + 4"))
        self.assertEqual(result.result, 10.0)
    
    def test_invalid_expression(self):
        with self.assertRaises(ValueError):
            calculate(CalculationInput(expression="invalid"))

if __name__ == '__main__':
    unittest.main()
```

### 2. Integration Testing

```python
import pytest
from utils.basetools import create_faq_tool, SearchInput

@pytest.fixture
def faq_tool():
    return create_faq_tool(collection_name="test_collection")

def test_faq_search(faq_tool):
    result = faq_tool(SearchInput(
        query="test query",
        limit=3
    ))
    
    assert isinstance(result.results, list)
    assert len(result.results) <= 3
```

## Tool Monitoring và Logging

### 1. Tool Usage Tracking

```python
import logging
from functools import wraps

def track_tool_usage(func):
    """Decorator to track tool usage statistics."""
    
    @wraps(func)
    def wrapper(*args, **kwargs):
        tool_name = func.__name__
        start_time = time.time()
        
        try:
            result = func(*args, **kwargs)
            execution_time = time.time() - start_time
            
            logging.info(f"Tool {tool_name} executed successfully in {execution_time:.2f}s")
            return result
            
        except Exception as e:
            execution_time = time.time() - start_time
            logging.error(f"Tool {tool_name} failed after {execution_time:.2f}s: {str(e)}")
            raise
    
    return wrapper

@track_tool_usage
def my_tracked_tool(input: MyToolInput) -> MyToolOutput:
    # Tool implementation
    pass
```

### 2. Performance Monitoring

```python
import psutil
import time

def performance_monitor(func):
    """Monitor tool performance metrics."""
    
    @wraps(func)
    def wrapper(*args, **kwargs):
        # Get initial metrics
        process = psutil.Process()
        cpu_before = process.cpu_percent()
        memory_before = process.memory_info().rss / 1024 / 1024  # MB
        
        start_time = time.time()
        
        try:
            result = func(*args, **kwargs)
            
            # Get final metrics
            execution_time = time.time() - start_time
            cpu_after = process.cpu_percent()
            memory_after = process.memory_info().rss / 1024 / 1024  # MB
            
            # Log performance metrics
            logging.info(f"Tool {func.__name__} performance:")
            logging.info(f"  Execution time: {execution_time:.2f}s")
            logging.info(f"  CPU usage: {cpu_after:.1f}%")
            logging.info(f"  Memory usage: {memory_after:.1f}MB")
            
            return result
            
        except Exception as e:
            logging.error(f"Tool {func.__name__} failed: {str(e)}")
            raise
    
    return wrapper
```

Với hệ thống tools này, bạn có thể xây dựng các AI agents rất mạnh mẽ và linh hoạt cho nhiều use cases khác nhau!
