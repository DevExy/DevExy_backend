from pydantic import BaseModel, EmailStr, field_validator, ConfigDict
from typing import Optional
from datetime import datetime

class UserBase(BaseModel):
    username: str
    email: EmailStr
    full_name: str
    github_username: Optional[str] = None

class UserCreate(UserBase):
    password: str
    confirm_password: str

    @field_validator('confirm_password')
    def passwords_match(cls, v, info):
        if v != info.data['password']:
            raise ValueError('Passwords do not match')
        return v

class UserLogin(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    user_id: int

class User(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None
    github_username: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)

class UserUpdateWithPassword(UserUpdate):
    password: Optional[str] = None
    confirm_password: Optional[str] = None
    
    @field_validator('confirm_password')
    def passwords_match(cls, v, info):
        if 'password' in info.data and info.data['password'] is not None:
            if v != info.data['password']:
                raise ValueError('Passwords do not match')
        return v