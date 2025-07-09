import redis
import uuid
from datetime import datetime
import chainlit as cl


class ShortTermMemory:
    """Manages user sessions and conversation memory with Redis backend"""

    def __init__(self, host="localhost", port=6379, db=0, max_messages=15):
        # Initialize Redis client
        self.redis_client = redis.StrictRedis(host=host, port=port, db=db)
        self.max_messages = max_messages  # Maximum number of messages to store

    def store(self, key: str, message: str):
        """Store a message in Redis, keeping only the latest 'max_messages' messages."""
        # Push the new message to the list (LPUSH puts it at the front)
        self.redis_client.lpush(key, message)

        # Trim the list to ensure it doesn't exceed the max size
        self.redis_client.ltrim(key, 0, self.max_messages - 1)
        print(
            f"Stored message: {message} for key: {key}. Total messages: {self.redis_client.llen(key)}"
        )

    def retrieve(self, key: str):
        """Retrieve all messages from Redis for a session (key)."""
        messages = self.redis_client.lrange(key, 0, -1)
        return [
            msg.decode("utf-8") for msg in messages
        ]  # Decode each message from bytes

    def delete(self, key: str):
        """Delete all messages for a given key."""
        self.redis_client.delete(key)
        print(f"Deleted all messages for key: {key}")

    def get_session_key(self):
        """Get or create session key"""
        session_key = cl.user_session.get("session_key")
        if not session_key:
            session_key = (
                f"user_{str(uuid.uuid4())[:8]}_{datetime.now().strftime('%Y%m%d_%H%M')}"
            )
            cl.user_session.set("session_key", session_key)
        return session_key

    def get_history_context(self, session_key):
        """Build conversation history context"""
        history = self.retrieve(session_key)
        if len(history) == 0:
            return ""

        # Redis LPUSH puts newest first, so reverse to get chronological order
        # Take up to 8 most recent messages in chronological order
        recent = list(reversed(history))[:8]
        context = "\n=== CONVERSATION HISTORY ===\n"
        if len(history) > 8:
            context += "[Showing last 8 messages]\n"

        return context + "\n".join(recent) + "\n=== END HISTORY ===\n\n"

    def store_message(self, session_key, role, content):
        """Store a message with timestamp"""
        timestamp = datetime.now().strftime("%H:%M")
        self.store(session_key, f"[{timestamp}] {role}: {content}")

    def store_user_message(self, session_key, content):
        """Store user message"""
        self.store_message(session_key, "User", content)

    def store_bot_message(self, session_key, content):
        """Store bot message"""
        self.store_message(session_key, "Bot", content)

    def store_error_message(self, session_key, error):
        """Store error message"""
        self.store_message(session_key, "System", f"Error - {str(error)}")

    def update_message_count(self):
        """Update and return message count"""
        count = (cl.user_session.get("message_count") or 0) + 1
        cl.user_session.set("message_count", count)
        return count


def test_session_manager():
    """Test function for SessionManager"""
    # Create an instance of the SessionManager class with max 3 messages
    manager = ShortTermMemory(max_messages=3)

    session_key = "user_1234_session"  # The unique key for this user session

    # Simulate storing some messages
    print("Storing messages...")
    manager.store(session_key, "Message 1: User asks about account balance.")
    manager.store(session_key, "Message 2: User asks for recent transactions.")
    manager.store(session_key, "Message 3: User asks for support contact info.")

    # Retrieve the stored messages and print
    print("Messages after storing 3:")
    print(manager.retrieve(session_key))

    # Simulate adding a 4th message (this should remove the oldest message)
    print("Storing 4th message...")
    manager.store(session_key, "Message 4: User asks for last month's bill.")

    # Retrieve and print the messages after the 4th message is added
    print("Messages after storing the 4th message (oldest removed):")
    print(manager.retrieve(session_key))

    # Clear all memory for the session
    print("Clearing memory...")
    manager.delete(session_key)
    print(f"Memory for {session_key} after clearing:")
    print(manager.retrieve(session_key))


# Call the test function when run directly
if __name__ == "__main__":
    test_session_manager()
