import os
from dotenv import load_dotenv
from pathlib import Path
from pydantic_settings import BaseSettings

load_dotenv()

class Settings(BaseSettings):
    # JWT settings
    SECRET_KEY: str = os.environ.get("SECRET_KEY", "your-secret-key-change-in-production")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    

settings = Settings()