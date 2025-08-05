
# Folder: cache

This folder provides a **short-term conversation memory** mechanism for the chatbot.  
Its main purpose is to **retain recent conversation history** so the bot can respond with proper context.

## File: `memory_handler.py`

### Purpose
- Handles **short-term memory** for user conversations.
- Provides a simple API to **retrieve history**, **store bot responses**, and **log errors**.
- Separates memory logic from the main codebase for better readability and maintainability.

### `class MessageMemoryHandler`

Acts as a **wrapper** around `ShortTermMemory` (from `redis_cache.py`) to simplify usage.

#### `__init__(max_messages: int = 15)`
- **Purpose:** Initializes the memory handler and creates a `ShortTermMemory` instance with a message retention limit.
- **Parameters:**
  - `max_messages` *(int)*: Maximum number of messages stored per session (default **15**).

#### `get_history_message(message_content: str) -> str`
- **Purpose:**
  - Retrieves recent conversation history from Redis.
  - Combines it with the user’s current message to form a **contextual message**.
  - Stores the new user message in memory.
- **Input:**  
  - `message_content`: The latest user message.
- **Output:**  
  - A string containing **conversation history + the current question**.
- **How it works:**
  1. Retrieves the `session_key`.
  2. Updates the message count for the session.
  3. Fetches history via `get_history_context()` and appends:
     ```
     CURRENT QUESTION: <message_content>
     ```
  4. Saves the new user message into Redis.

#### `store_bot_response(response: str) -> None`
- **Purpose:** Stores the bot’s response in memory.
- **Input:** `response` - the bot’s reply.

#### `store_error(error: Exception) -> None`
- **Purpose:** Logs an error message into memory for debugging.
- **Input:** `error` - an Exception object.

---

##  File: `redis_cache.py`

###  Purpose
- Provides a **Redis-backed storage** for short-term conversation memory.
- Manages user sessions and enforces a **maximum message retention** policy.
- Supports retrieving and formatting history for contextual responses.

###  `class ShortTermMemory`

Manages **session keys**, and handles storing, retrieving, and trimming messages in Redis.

#### `__init__(host="localhost", port=6379, db=0, max_messages=15)`
- **Purpose:** Initializes Redis connection and sets up message retention limits.
- **Parameters:**
  - `host`, `port`, `db` – Redis connection details.
  - `max_messages` – maximum number of messages per session.

#### `store(key: str, message: str) -> None`
- **Purpose:** Pushes a new message into Redis.
- **Behavior:**
  - Uses `LPUSH` to prepend a message.
  - Uses `LTRIM` to ensure only **the latest `max_messages`** are kept.
  - Prints a debug log with the stored message and total count.

#### `retrieve(key: str) -> List[str]`
- **Purpose:** Fetches all stored messages for a given session key.
- **Output:** A list of decoded messages (UTF-8).

#### `delete(key: str) -> None`
- **Purpose:** Deletes all stored messages for a given session.

#### `get_session_key() -> str`
- **Purpose:** Retrieves the current `session_key` or creates a new one.
- **Behavior:**
  - Checks `cl.user_session` for an existing session.
  - If none exists, generates a new key:
    ```
    user_<UUID_8chars>_<YYYYMMDD_HHMM>
    ```
  - Saves it to `cl.user_session`.

#### `get_history_context(session_key: str) -> str`
- **Purpose:** Builds a formatted conversation history string.
- **Behavior:**
  - Retrieves all messages for the session.
  - If there are more than 8, only the **last 8 messages** are shown.
  - Wraps history with:
    ```
    === CONVERSATION HISTOR
