
# 📂 Folder: prompts

This folder contains **prompt templates and scripts** used for configuring and testing LLM-based agents.

It currently includes the following files:

* `__init__.py` → Marks this folder as a Python package, enabling imports from `prompts`.
* `demo.py` → Likely contains a **demo script** to test or showcase how prompts are used.
* `mini_qa_agent_prompt.py` → Contains **prompt templates and logic** for a **mini QA (Question-Answering) agent**, possibly defining system, user, and assistant messages.

---

## ✅ Purpose of the folder

* Centralizes **prompt engineering** components.
* Provides **reusable prompt templates** for different agent behaviors.
* Enables **easy testing** (`demo.py`) and modular use of prompt templates in other modules.

---

## ✅ Typical usage

* Other modules (like Milvus indexing, embedding engine, or chatbot pipelines) may **import prompt templates** from this folder.
* `demo.py` might be used for quick local testing:

  ```bash
  python prompts/demo.py
  ```
* `mini_qa_agent_prompt.py` might define:

  ```python
  SYSTEM_PROMPT = "You are a helpful QA assistant..."
  ```

---

