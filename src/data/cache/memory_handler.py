"""
Memory Handler - Handle messages with short-term memory
Separate complex logic to make main code readable
"""

from data.cache.redis_cache import ShortTermMemory


class MessageMemoryHandler:
    """Handle memory only - no AI logic"""
    
    def __init__(self, max_messages: int = 15):
        self.session_manager = ShortTermMemory(max_messages=max_messages)
    
    def get_history_message(self, message_content: str) -> str:
        """
        Prepare message with context from memory
        
        Args:
            message_content: User message content
            
        Returns:
            str: Message with history context added
        """
        session_key = self.session_manager.get_session_key()
        self.session_manager.update_message_count()
        
        context = self.session_manager.get_history_context(session_key)
        full_message = f"{context}CURRENT REQUEST: {message_content}"
        
        self.session_manager.store_user_message(session_key, message_content)
        
        return full_message
    
    def store_bot_response(self, response: str):
        """Store bot response to memory"""
        session_key = self.session_manager.get_session_key()
        self.session_manager.store_bot_message(session_key, response)
    
    def store_error(self, error: Exception):
        """Store error to memory"""
        session_key = self.session_manager.get_session_key()
        self.session_manager.store_error_message(session_key, error)
