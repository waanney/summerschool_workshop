erom datetime import datetime
from zoneinfo import ZoneInfo
import os
from dotenv import load_dotenv


class Settings:
    """Settings for the chatbot service."""

    def __init__(self):
        # Load environment variables from .env file first
        env_file = os.getenv("ENVIRONMENT_FILE", ".env")
        load_dotenv(env_file)
        # Now we can access environment variables

        self.APP_NAME: str = "Chatbot API"
        self.DEBUG: bool = True
        self.API_VERSION: str = "v1"
        self.HOST: str = os.getenv("API_HOST", "127.0.0.1")
        self.PORT: int = int(os.getenv("API_PORT", 7000))
        self.TIMEZONE: str = "UTC"  # Default timezone

        # Milvus settings
        self.MILVUS_URL = os.getenv(
            "MILVUS_URI"
        )  # Using MILVUS_URI to match .env.template
        self.MILVUS_TOKEN = os.getenv("MILVUS_TOKEN")

        # Model serving settings
        self.OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "EMPTY")

        self.LOG_LEVEL: str = "INFO"
        self.LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        self.LOG_FILE: str = "logs/chatbot.log"

        self.RATE_LIMIT_PER_MINUTE: int = 60

    def get_current_time(self) -> datetime:
        """
        Returns the current time in the specified timezone.
        """
        return datetime.now(ZoneInfo(self.TIMEZONE))


settings = Settings()
