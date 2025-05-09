from pydantic import BaseModel

class Settings(BaseModel):
    DATABASE_URL: str = "sqlite:///./sql_app.db"
    SECRET_KEY: str = "your-secret-key"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    class Config:
        env_file = ".env"

settings = Settings()