from pydantic import BaseModel, EmailStr, Field

class UserBase(BaseModel):
    email: EmailStr

class UserCreate(UserBase):
    password: str = Field(..., min_length=6)

class User(UserBase):
    id: int
    is_active: bool
   
    class Config:
        from_attributes = True