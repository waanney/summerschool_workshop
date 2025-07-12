# Hướng dẫn sử dụng MCP Tools với PydanticAI

## Giới thiệu

Model Context Protocol (MCP) là một giao thức mở cho phép các ứng dụng AI tích hợp với các công cụ và nguồn dữ liệu bên ngoài. PydanticAI hỗ trợ làm MCP client để kết nối với các MCP server và sử dụng các tools của chúng.

## Cài đặt

### Yêu cầu hệ thống
- Python 3.10 trở lên
- PydanticAI hoặc PydanticAI-slim với MCP extension

### Cài đặt package

```bash
# Cài đặt PydanticAI với MCP support
pip install "pydantic-ai-slim[mcp]"

# Hoặc cài đặt full version
pip install pydantic-ai
```

## Các loại MCP Client

PydanticAI hỗ trợ 3 loại transport để kết nối với MCP server:

### 1. SSE Client (Server-Sent Events)
- Kết nối qua HTTP với SSE transport
- Server phải đang chạy trước khi client kết nối

### 2. Streamable HTTP Client
- Kết nối qua HTTP với Streamable HTTP transport
- Hiệu suất cao hơn SSE

### 3. Stdio Client
- Chạy server như một subprocess
- Giao tiếp qua stdin/stdout

## Hướng dẫn sử dụng từng loại

### 1. SSE Client

#### Bước 1: Chạy MCP Server
```bash
# Chạy server bằng Deno
deno run -N -R=node_modules -W=node_modules --node-modules-dir=auto jsr:@pydantic/mcp-run-python sse
```

#### Bước 2: Tạo Client
```python
from pydantic_ai import Agent
from pydantic_ai.mcp import MCPServerSSE
import asyncio

# Tạo server connection
server = MCPServerSSE(url='http://localhost:3001/sse')

# Tạo agent với MCP server
agent = Agent('openai:gpt-4o', mcp_servers=[server])

async def main():
    async with agent.run_mcp_servers():
        result = await agent.run('How many days between 2000-01-01 and 2025-03-18?')
    print(result.output)
    # Output: There are 9,208 days between January 1, 2000, and March 18, 2025.

# Chạy chương trình
asyncio.run(main())
```

### 2. Streamable HTTP Client

#### Bước 1: Tạo MCP Server
```python
# streamable_http_server.py
from mcp.server.fastmcp import FastMCP

app = FastMCP()

@app.tool()
def add(a: int, b: int) -> int:
    """Cộng hai số"""
    return a + b

if __name__ == '__main__':
    app.run(transport='streamable-http')
```

#### Bước 2: Tạo Client
```python
from pydantic_ai import Agent
from pydantic_ai.mcp import MCPServerStreamableHTTP
import asyncio

# Tạo server connection
server = MCPServerStreamableHTTP('http://localhost:8000/mcp')

# Tạo agent với MCP server
agent = Agent('openai:gpt-4o', mcp_servers=[server])

async def main():
    async with agent.run_mcp_servers():
        result = await agent.run('Calculate 15 + 27')
    print(result.output)

asyncio.run(main())
```

### 3. Stdio Client

```python
from pydantic_ai import Agent
from pydantic_ai.mcp import MCPServerStdio
import asyncio

# Tạo server connection với stdio transport
server = MCPServerStdio(
    'deno',
    args=[
        'run',
        '-N',
        '-R=node_modules',
        '-W=node_modules',
        '--node-modules-dir=auto',
        'jsr:@pydantic/mcp-run-python',
        'stdio',
    ]
)

agent = Agent('openai:gpt-4o', mcp_servers=[server])

async def main():
    async with agent.run_mcp_servers():
        result = await agent.run('Calculate the square root of 144')
    print(result.output)

asyncio.run(main())
```

## Tính năng nâng cao

### 1. Tool Call Customization

Bạn có thể tùy chỉnh cách tool được gọi bằng cách sử dụng `process_tool_call`:

```python
from typing import Any
from pydantic_ai import Agent
from pydantic_ai.mcp import CallToolFunc, MCPServerStdio, ToolResult
from pydantic_ai.tools import RunContext

async def process_tool_call(
    ctx: RunContext[int],
    call_tool: CallToolFunc,
    tool_name: str,
    args: dict[str, Any],
) -> ToolResult:
    """Xử lý tool call và truyền thêm metadata"""
    return await call_tool(tool_name, args, metadata={'deps': ctx.deps})

server = MCPServerStdio(
    'python', 
    ['mcp_server.py'], 
    process_tool_call=process_tool_call
)

agent = Agent(
    model='openai:gpt-4o',
    deps_type=int,
    mcp_servers=[server]
)
```

### 2. Tool Prefixes - Tránh xung đột tên

Khi sử dụng nhiều MCP server có tool cùng tên, bạn có thể sử dụng `tool_prefix`:

```python
from pydantic_ai import Agent
from pydantic_ai.mcp import MCPServerSSE

# Tạo server với prefix khác nhau
weather_server = MCPServerSSE(
    url='http://localhost:3001/sse',
    tool_prefix='weather'  # Tools sẽ có prefix 'weather_'
)

calculator_server = MCPServerSSE(
    url='http://localhost:3002/sse',
    tool_prefix='calc'     # Tools sẽ có prefix 'calc_'
)

# Nếu cả hai server có tool 'get_data', chúng sẽ được hiển thị như:
# - 'weather_get_data'
# - 'calc_get_data'
agent = Agent('openai:gpt-4o', mcp_servers=[weather_server, calculator_server])
```

### 3. MCP Sampling

MCP Sampling cho phép MCP server thực hiện LLM calls thông qua client:

```python
from pydantic_ai import Agent
from pydantic_ai.mcp import MCPServerStdio

# Server hỗ trợ sampling
server = MCPServerStdio(command='python', args=['generate_svg.py'])
agent = Agent('openai:gpt-4o', mcp_servers=[server])

async def main():
    async with agent.run_mcp_servers():
        result = await agent.run('Create an image of a robot in a punk style.')
    print(result.output)
    # Output: Image file written to robot_punk.svg.

# Vô hiệu hóa sampling nếu cần
server_no_sampling = MCPServerStdio(
    command='python',
    args=['generate_svg.py'],
    allow_sampling=False,  # Không cho phép sampling
)
```

## Debug và Monitoring

### Sử dụng Logfire để debug

```python
import logfire
from pydantic_ai import Agent
from pydantic_ai.mcp import MCPServerSSE

# Cấu hình logfire
logfire.configure()
logfire.instrument_pydantic_ai()

server = MCPServerSSE(url='http://localhost:3001/sse')
agent = Agent('openai:gpt-4o', mcp_servers=[server])

async def main():
    async with agent.run_mcp_servers():
        result = await agent.run('Calculate 2 + 2')
    print(result.output)
```

## Ví dụ thực tế

### Tạo một MCP Tool đơn giản

```python
# mcp_calculator_server.py
from mcp.server.fastmcp import FastMCP
import math

app = FastMCP()

@app.tool()
def add(a: float, b: float) -> float:
    """Cộng hai số"""
    return a + b

@app.tool()
def multiply(a: float, b: float) -> float:
    """Nhân hai số"""
    return a * b

@app.tool()
def square_root(number: float) -> float:
    """Tính căn bậc hai"""
    if number < 0:
        raise ValueError("Không thể tính căn bậc hai của số âm")
    return math.sqrt(number)

@app.tool()
def power(base: float, exponent: float) -> float:
    """Tính lũy thừa"""
    return base ** exponent

if __name__ == '__main__':
    app.run(transport='streamable-http', port=8000)
```

### Client sử dụng Calculator Server

```python
# mcp_calculator_client.py
from pydantic_ai import Agent
from pydantic_ai.mcp import MCPServerStreamableHTTP
import asyncio

async def main():
    # Kết nối với calculator server
    server = MCPServerStreamableHTTP('http://localhost:8000/mcp')
    agent = Agent('openai:gpt-4o', mcp_servers=[server])
    
    async with agent.run_mcp_servers():
        # Thử nghiệm các phép tính
        questions = [
            "What is 15 + 27?",
            "Calculate the square root of 144",
            "What is 2 to the power of 8?",
            "Multiply 7 by 9"
        ]
        
        for question in questions:
            result = await agent.run(question)
            print(f"Q: {question}")
            print(f"A: {result.output}\n")

if __name__ == '__main__':
    asyncio.run(main())
```

## Troubleshooting

### Lỗi thường gặp

1. **Connection refused**: Đảm bảo MCP server đang chạy trước khi client kết nối
2. **Tool not found**: Kiểm tra tool name và prefix
3. **Timeout**: Tăng timeout cho connection
4. **Import error**: Đảm bảo đã cài đặt đúng dependencies

### Tips và Best Practices

1. **Luôn sử dụng async context manager** với `agent.run_mcp_servers()`
2. **Sử dụng tool prefixes** khi có nhiều server với tool cùng tên
3. **Xử lý errors** một cách graceful
4. **Sử dụng type hints** cho tools để AI hiểu rõ hơn
5. **Viết documentation** rõ ràng cho từng tool

## Kết luận

MCP Tools với PydanticAI cung cấp một cách mạnh mẽ để mở rộng khả năng của AI agents. Với hướng dẫn này, bạn có thể:

- Tạo và sử dụng các MCP tools
- Kết nối với các MCP server khác nhau
- Tùy chỉnh tool calls theo nhu cầu
- Debug và monitor hoạt động của tools

Bắt đầu với các ví dụ đơn giản và dần dần mở rộng để tạo ra các tools phức tạp hơn phù hợp với use case của bạn.