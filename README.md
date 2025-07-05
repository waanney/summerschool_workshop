# summerschool_workshop

A private Python-based project for experimenting with advanced data retrieval and conversational AI workflows. The repository focuses on integrating semantic search, vector databases, memory caching, and large language models (LLMs) for question-answering and agent-driven interaction.

## Features

- **Short-Term Memory with Redis**  
  Implements a `ShortTermMemory` class to store and retrieve recent chat or session messages in Redis, keeping only the latest N messages per session (see `src/data/cache/redis_cache.py`).

- **Vector Database Integration (Milvus)**  
  Provides a `MilvusClient` for indexing and searching question-answer pairs using dense and sparse embeddings. Supports hybrid semantic/BM25 search and flexible schema (see `src/data/milvus/milvus_client.py`).

- **Embeddings Engine**  
  Wraps OpenAI embedding models for text/vector conversion, with state-saving/load capabilities (see `src/data/embeddings/embedder.py`).

- **Conversational Agent Demo**  
  Example workflow using Chainlit, Google Gemini (via `pydantic_ai`), and agent orchestration for real-time chat, with support for tools and prompts (see `workflow/demo.py`).

- **Utilities**  
  Includes helper scripts for logging and date tools.

## Setup

1. **Clone the repository**  
   ```
   git clone https://github.com/waanney/summerschool_workshop.git
   cd summerschool_workshop
   ```

2. **Install dependencies**  
   Recommended to use a virtual environment.
   ```
   pip install .  
   ```

3. **Environment Variables**  
   Set the following environment variables as needed:
   - `GEMINI_API_KEY` (for Google Gemini)
   - `MILVUS_URI`, `MILVUS_TOKEN` (for Milvus vector DB)
   - Redis connection details (if not default)

4. **Run a Demo**  
   To start the conversational demo (requires Chainlit):
   ```
   chainlit run workflow/demo.py
   ```

## Project Structure

```
src/
  data/
    cache/         # Redis-powered short-term memory
    embeddings/    # OpenAI embeddings utilities
    milvus/        # Milvus vector DB client
  utils/           # Logging, helper utilities
workflow/
  demo.py          # Chainlit + Gemini agent demo
```

## Usage Examples

- **Short-term chat memory:**  
  Store and retrieve the latest N messages per user session.
- **Vector search:**  
  Index FAQs and perform hybrid dense/sparse retrieval using Milvus.
- **Conversational agent:**  
  Integrate LLM, tools, and memory for interactive Q&A.

## License

This repository is private and for educational or experimental use only.

---

> **Note:**  
> This README was generated based on source code structure and may need further customization for your specific workshop or use case.
