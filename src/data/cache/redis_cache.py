import redis

class ShortTermMemory:
    def __init__(self, host='localhost', port=6379, db=0, max_messages=5):
        # Initialize Redis client
        self.redis_client = redis.StrictRedis(host=host, port=port, db=db)
        self.max_messages = max_messages  # Maximum number of messages to store

    def store(self, key: str, message: str):
        """Store a message in Redis, keeping only the latest 'max_messages' messages."""
        # Push the new message to the list (LPUSH puts it at the front)
        self.redis_client.lpush(key, message)
        
        # Trim the list to ensure it doesn't exceed the max size
        self.redis_client.ltrim(key, 0, self.max_messages - 1)
        print(f"Stored message: {message} for key: {key}. Total messages: {self.redis_client.llen(key)}")

    def retrieve(self, key: str):
        """Retrieve all messages from Redis for a session (key)."""
        messages = self.redis_client.lrange(key, 0, -1)
        return [msg.decode('utf-8') for msg in messages]  # Decode each message from bytes

    def delete(self, key: str):
        """Delete all messages for a given key."""
        self.redis_client.delete(key)
        print(f"Deleted all messages for key: {key}")




def test_short_term_memory():
    # Create an instance of the ShortTermMemory class with max 3 messages
    memory = ShortTermMemory(max_messages=3)  # TTL is not used, only message count
    
    session_key = "user_1234_session"  # The unique key for this user session
    
    # Simulate storing some messages
    print("Storing messages...")
    memory.store(session_key, "Message 1: User asks about account balance.")
    memory.store(session_key, "Message 2: User asks for recent transactions.")
    memory.store(session_key, "Message 3: User asks for support contact info.")
    
    # Retrieve the stored messages and print
    print("Messages after storing 3:")
    print(memory.retrieve(session_key))
    
    # Simulate adding a 4th message (this should remove the oldest message)
    print("Storing 4th message...")
    memory.store(session_key, "Message 4: User asks for last month’s bill.")

    # Retrieve and print the messages after the 4th message is added
    print("Messages after storing the 4th message (oldest removed):")
    print(memory.retrieve(session_key))
    
    # Clear all memory for the session
    print("Clearing memory...")
    memory.delete(session_key)
    print(f"Memory for {session_key} after clearing:")
    print(memory.retrieve(session_key))

# Call the test function
test_short_term_memory()
