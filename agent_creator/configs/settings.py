from os import getenv
from threading import Lock

from dotenv import load_dotenv


class Settings:
    _instance = None
    _lock = Lock()  # for thread-safe singleton

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return  # Prevent reinitialization in singleton

        # Load environment variables from .env file
        load_dotenv()

        # Add your environment variables
        # self.WATSONX_API_KEY: str = getenv("WATSONX_API_KEY", "")
        # self.PROJECT_ID: str = getenv("PROJECT_ID", "")
        # self.WATSONX_URL: str = getenv("WATSONX_URL", "")

        # self.PORT: int = int(getenv("PORT", "8000"))

        self.debug_mode = getenv("DEBUG_MODE", "False").lower() in ("true", "1", "t")

        self._initialized = True  # Mark as initialized to prevent re-running init


if __name__ == "__main__":
    # Usage:
    settings = Settings()
    print(settings)
