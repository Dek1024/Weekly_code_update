from pydantic_settings import BaseSettings
from pathlib import Path
env_path = "./app/.env"

class Settings(BaseSettings):
    openai_key: str
    grokai_key: str
    mistralai_key: str

    class Config:
        env_file = env_path

settings = Settings()