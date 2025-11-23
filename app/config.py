from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    DATABASE_URL: str
    FHIR_SERVER_URL: str
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    APP_NAME: str = "Sistema Clínico Interoperable"
    DEBUG: bool = True

    class Config:
        env_file = "/opt/clinica-fhir/.env"

@lru_cache
def get_settings():
    return Settings()

settings = get_settings()
