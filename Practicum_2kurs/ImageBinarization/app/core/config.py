from pydantic import BaseModel, Field, RedisDsn

class Settings(BaseModel):
    '''
    Класс Settings используется для хранения конфигурационных параметров приложения
    '''
    # URL для подключения к базе данных 
    DATABASE_URL: str = Field(default="sqlite:///C:\\Users\\nasty\\Practicum_2kurs\\ImageBinarization\\DB.db")
  
    # Секретный ключ для шифрования и подписи JWT-токенов
    SECRET_KEY: str = Field(default="AagB7544")

    REDIS_URL: RedisDsn = Field(default="redis://localhost:6379/0")

    # Алгоритм, используемый для шифрования JWT-токенов (по умолчанию HS256)
    ALGORITHM: str = Field(default="HS256")

    # Время жизни access-токена в минутах
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30)

    # Вложенный класс Config для дополнительных настроек Pydantic
    class Config:
        env_file = ".env"
        extra = "ignore"

# Создаем экземпляр класса Settings для использования в приложении
settings = Settings()