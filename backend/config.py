import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    PROJECT_NAME = "对话机器人"
    VERSION = "1.0.0"
    DEBUG = os.getenv("DEBUG", "False").lower() == "true"
    
    DASHSCOPE_API_KEY = os.getenv("DASHSCOPE_API_KEY", "")
    
    CHROMA_DB_PATH = os.getenv("CHROMA_DB_PATH", "./chroma_db")
    
    MAX_SESSION_MESSAGES = int(os.getenv("MAX_SESSION_MESSAGES", "50"))
    
    API_PREFIX = os.getenv("API_PREFIX", "/api")

settings = Settings()