from pydantic import BaseModel, EmailStr, Field
from typing import Optional

class User(BaseModel):
    email: EmailStr

class UserCreate(User):
    password: str

class UserLogin(User):
    password: str

class UserMeResponse(BaseModel):
    id: int
    email: str
    token: Optional[str] = None
    
    class Config:
        from_attributes = True