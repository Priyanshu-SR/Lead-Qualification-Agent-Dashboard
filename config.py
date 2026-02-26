from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    MONGO_URI: str = "mongodb+srv://dashboardUser:dashboardUser12345@whatsappbot.qn3amlt.mongodb.net/"
    MONGO_DB: str = "Yamini"
    MONGO_COLLECTION: str = "customerChats"
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    CORS_ORIGINS: List[str] = ["*"]

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()
