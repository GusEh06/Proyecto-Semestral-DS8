from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "postgresql://postgres:shiroapa1805*@localhost:5432/restaurante_db"

    # JWT
    SECRET_KEY: str = "y6f9f38c64854372c28a705d8d0535539f4c45b60cef86353010248eee4293386"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # API
    API_V1_PREFIX: str = "/api/v1"
    PROJECT_NAME: str = "Sistema de Reservaciones"

    # CORS
<<<<<<< HEAD
    ALLOWED_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:5173","http://localhost:4321"]
=======
    ALLOWED_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:5173", "http://localhost:4321"]
>>>>>>> dc896348bbac8783ca4cada62bc18db695485039

    class Config:
        env_file = ".env"


settings = Settings()
