from redis import Redis
import uuid
from datetime import datetime
import chainlit as cl
import redis
from typing import List


class ShortTermMemory:
    """Manages user sessions and conversation memory with Redis backend"""

    def __init__(
        self,
        host: str = "localhost",
        port: int = 6379,
        db: int = 0,
        max_messages: int = 15,
    ):
        self.redis_client: Redis = redis.StrictRedis(host=host, port=port, db=db)
        self.max_messages = max_messages

    def store(self, key: str, message: str) -> None:
        """Store a message in Redis, keeping only the latest 'max_messages' messages."""
        self.redis_client.lpush(key, message)

        # Trim the list to ensure it doesn't exceed the max size
        self.redis_client.ltrim(key, 0, self.max_messages - 1)
        print(
            f"Stored message: {message} for key: {key}. Total messages: {self.redis_client.llen(key)}"
        )

    def retrieve(self, key: str) -> List[str]:
        messages = self.redis_client.lrange(key, 0, -1) or []
        return [
            msg.decode("utf-8") if isinstance(msg, bytes) else msg for msg in messages  # type: ignore
        ]

    def delete(self, key: str) -> None:
        """Delete all messages for a given key."""
        self.redis_client.delete(key)
        print(f"Deleted all messages for key: {key}")

    def get_session_key(self) -> str:
        """Get or create session key"""
        session_key = cl.user_session.get("session_key")  # type: ignore
        if not session_key:
            session_key = (
                f"user_{str(uuid.uuid4())[:8]}_{datetime.now().strftime('%Y%m%d_%H%M')}"
            )
            cl.user_session.set("session_key", session_key)  # type: ignore
        return str(session_key) if isinstance(session_key, str) else ""

    def get_history_context(self, session_key: str) -> str:
        """Build conversation history context"""
        history = self.retrieve(session_key)
        if len(history) == 0:
            return ""

        recent = list(reversed(history))[:8]
        context = "\n=== CONVERSATION HISTORY ===\n"
        if len(history) > 8:
            context += "[Showing last 8 messages]\n"

        return context + "\n".join(recent) + "\n=== END HISTORY ===\n\n"

    def store_message(self, session_key: str, role: str, content: str) -> None:
        """Store a message with timestamp"""
        timestamp = datetime.now().strftime("%H:%M")
        self.store(session_key, f"[{timestamp}] {role}: {content}")

    def store_user_message(self, session_key: str, content: str) -> None:
        """Store user message"""
        self.store_message(session_key, "User", content)

    def store_bot_message(self, session_key: str, content: str) -> None:
        """Store bot message"""
        self.store_message(session_key, "Bot", content)

    def store_error_message(self, session_key: str, error: str) -> None:
        """Store error message"""
        self.store_message(session_key, "System", f"Error - {str(error)}")

    def update_message_count(self) -> int:
        """Update and return message count"""
        count = (cl.user_session.get("message_count") or 0) + 1
        cl.user_session.set("message_count", count)
        return count
