
# Folder: llm

This folder contains **LLM (Large Language Model) client integrations and utilities**, focusing on model setup, agent creation, and tool integration.

It currently includes:

* `base.py` → Defines a generic `AgentClient` for creating LLM-powered agents with tools and system prompts.

---

## File: `base.py`

###  Purpose

* Provides a **base client for LLM agents** using the `pydantic_ai` framework.
* Integrates with **Google Gemini API** via `GoogleGLAProvider`.
* Uses `ShortTermMemory` (Redis-based) for maintaining limited session context.
* Allows creation of **custom agents** with system prompts and optional tools.

---

##  `class AgentClient`

A simple wrapper to configure and create a `pydantic_ai.Agent` instance.

### Attributes

* `model` → A `GeminiModel` instance (default: `gemini-2.0-flash`).
* `system_prompt` → A system prompt that defines the agent’s role and behavior.
* `tools` → A list of callable tools (functions) that the agent can use.

---

### **`__init__(system_prompt: str, tools: List[Callable], model: GeminiModel = model)`**

* **Purpose:** Initializes the agent client with a model, system prompt, and tools.
* **Parameters:**

  * `system_prompt` → Instructional prompt to guide the agent.
  * `tools` → List of callable functions that the agent can invoke.
  * `model` → (Optional) Custom `GeminiModel` instance, defaults to a preconfigured model.

---

### **`create_agent() -> Agent`**

* **Purpose:** Creates and returns a `pydantic_ai.Agent` instance.
* **Behavior:**

  1. Wraps the configured `GeminiModel` with the provided `system_prompt` and `tools`.
  2. Returns a ready-to-use `Agent`.

---

##  Additional Components

* **`provider`** → Uses `GoogleGLAProvider` with API key from environment (`GEMINI_API_KEY`).
* **`model`** → Preconfigured `GeminiModel` (`gemini-2.0-flash`).
* **`session_manager`** → Uses `ShortTermMemory` from `redis_cache` to handle **short-term chat history**.

---

##  Usage Example

```python
from llm.base import AgentClient

def sample_tool():
    return "Sample tool executed"

agent_client = AgentClient(
    system_prompt="You are a helpful assistant.",
    tools=[sample_tool]
)

agent = agent_client.create_agent()
response = agent.run("What is the weather today?")
print(response)
```

---

