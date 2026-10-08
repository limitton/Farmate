import os
from pydantic_settings import BaseSettings
import os
from dotenv import load_dotenv

class Settings(BaseSettings):
    OPENAI_API_URL: str = "https://clovastudio.stream.ntruss.com/v1/openai/"
    API_KEY: str = "nv-3f1151bb8f5d4e4a8df381283a84776bfKSG"

settings = Settings()
