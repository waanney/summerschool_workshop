
# MCP Tools Usage Guide with PydanticAI

## Introduction

Model Context Protocol (MCP) is an open protocol that allows AI applications to integrate with external tools and data sources. PydanticAI supports acting as an MCP client to connect to MCP servers and use their tools.

## Installation

### System Requirements

* Python 3.10 or higher
* PydanticAI or PydanticAI-slim with MCP extension

### Install the package

```bash
# Install PydanticAI with MCP support
pip install "pydantic-ai-slim[mcp]"

# Or install the full version
pip install pydantic-ai
```

## Available MCP Tools

[https://github.com/modelcontextprotocol/servers?tab=readme-ov-file](https://github.com/modelcontextprotocol/servers?tab=readme-ov-file)

## Types of MCP Clients

PydanticAI supports 3 types of transport to connect with MCP servers:

### 1. SSE Client (Server-Sent Events)

* Connects via HTTP using SSE transport
* Server must be running before the client connects

### 2. Streamable HTTP Client

* Connects via HTTP with Streamable HTTP transport
* Higher performance than SSE

### 3. Stdio Client

* Runs the server as a subprocess
* Communicates via stdin/stdout

## How to Use Each Type

### 1. SSE Client

#### Step 1: Run MCP Server

```bash
# Run the server using Deno
deno run -N -R=node_modules -W=node_modules --node-modules-dir=auto jsr:@pydantic/mcp-run-python sse
```

#### Step 2: Create Client

```python
from pydantic_ai import Agent
from pydantic_ai.mcp import MCPServerSSE
import asyncio

# Create server connection
server = MCPServerSSE(url='http://localhost:3001/sse')

# Create agent with MCP server
agent = Agent('openai:gpt-4o', mcp_servers=[server])

async def main():
    async with agent.run_mcp_servers():
        result = await agent.run('How many days between 2000-01-01 and 2025-03-18?')
    print(result.output)
    # Output: There are 9,208 days between January 1, 2000, and March 18, 2025.

# Run the program
asyncio.run(main())
```

### 2. Streamable HTTP Client

#### Step 1: Create MCP Server

```python
# streamable_http_server.py
from mcp.server.fastmcp import FastMCP

app = FastMCP()

@app.tool()
def add(a: int, b: int) -> int:
    """Add two numbers"""
    return a + b

if __name__ == '__main__':
    app.run(transport='streamable-http')
```

#### Step 2: Create Client

```python
from pydantic_ai import Agent
from pydantic_ai.mcp import MCPServerStreamableHTTP
import asyncio

# Create server connection
server = MCPServerStreamableHTTP('http://localhost:8000/mcp')

# Create agent with MCP server
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

# Create server connection with stdio transport
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

## Advanced Features

### 1. Tool Call Customization

You can customize how tools are called using `process_tool_call`:

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
    """Handle tool calls and pass additional metadata"""
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

### 2. Tool Prefixes - Avoid Name Conflicts

When using multiple MCP servers with tools of the same name, you can use `tool_prefix`:

```python
from pydantic_ai import Agent
from pydantic_ai.mcp import MCPServerSSE

# Create servers with different prefixes
weather_server = MCPServerSSE(
    url='http://localhost:3001/sse',
    tool_prefix='weather'  # Tools will have 'weather_' prefix
)

calculator_server = MCPServerSSE(
    url='http://localhost:3002/sse',
    tool_prefix='calc'     # Tools will have 'calc_' prefix
)

# If both servers have a tool 'get_data', they will appear as:
# - 'weather_get_data'
# - 'calc_get_data'
agent = Agent('openai:gpt-4o', mcp_servers=[weather_server, calculator_server])
```

### 3. MCP Sampling

MCP Sampling allows the MCP server to perform LLM calls through the client:

```python
from pydantic_ai import Agent
from pydantic_ai.mcp import MCPServerStdio

# Server supports sampling
server = MCPServerStdio(command='python', args=['generate_svg.py'])
agent = Agent('openai:gpt-4o', mcp_servers=[server])

async def main():
    async with agent.run_mcp_servers():
        result = await agent.run('Create an image of a robot in a punk style.')
    print(result.output)
    # Output: Image file written to robot_punk.svg.

# Disable sampling if needed
server_no_sampling = MCPServerStdio(
    command='python',
    args=['generate_svg.py'],
    allow_sampling=False,  # Disallow sampling
)
```

## Debugging and Monitoring

### Using Logfire for Debugging

```python
import logfire
from pydantic_ai import Agent
from pydantic_ai.mcp import MCPServerSSE

# Configure logfire
logfire.configure()
logfire.instrument_pydantic_ai()

server = MCPServerSSE(url='http://localhost:3001/sse')
agent = Agent('openai:gpt-4o', mcp_servers=[server])

async def main():
    async with agent.run_mcp_servers():
        result = await agent.run('Calculate 2 + 2')
    print(result.output)
```

## Real-World Example

### Create a Simple MCP Tool

```python
# mcp_calculator_server.py
from mcp.server.fastmcp import FastMCP
import math

app = FastMCP()

@app.tool()
def add(a: float, b: float) -> float:
    """Add two numbers"""
    return a + b

@app.tool()
def multiply(a: float, b: float) -> float:
    """Multiply two numbers"""
    return a * b

@app.tool()
def square_root(number: float) -> float:
    """Calculate square root"""
    if number < 0:
        raise ValueError("Cannot calculate square root of negative numbers")
    return math.sqrt(number)

@app.tool()
def power(base: float, exponent: float) -> float:
    """Calculate power"""
    return base ** exponent

if __name__ == '__main__':
    app.run(transport='streamable-http', port=8000)
```

### Client Using Calculator Server

```python
# mcp_calculator_client.py
from pydantic_ai import Agent
from pydantic_ai.mcp import MCPServerStreamableHTTP
import asyncio

async def main():
    # Connect to calculator server
    server = MCPServerStreamableHTTP('http://localhost:8000/mcp')
    agent = Agent('openai:gpt-4o', mcp_servers=[server])
    
    async with agent.run_mcp_servers():
        # Test calculations
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

### Common Errors

1. **Connection refused**: Ensure the MCP server is running before the client connects.
2. **Tool not found**: Check tool name and prefix.
3. **Timeout**: Increase the connection timeout.
4. **Import error**: Ensure all dependencies are installed correctly.

### Tips and Best Practices

1. **Always use async context manager** with `agent.run_mcp_servers()`.
2. **Use tool prefixes** when multiple servers have tools with the same name.
3. **Handle errors gracefully**.
4. **Use type hints** for tools to help AI understand them better.
5. **Write clear documentation** for each tool.

## Conclusion

MCP Tools with PydanticAI provide a powerful way to extend AI agent capabilities. With this guide, you can:

* Create and use MCP tools
* Connect to different MCP servers
* Customize tool calls as needed
* Debug and monitor tool activity

Start with simple examples and gradually expand to create more complex tools tailored to your use case.
