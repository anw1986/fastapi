from pydantic import BaseModel, EmailStr, ValidationError,validator
from typing import Optional
from datetime import datetime
from pydantic.types import conint

# model for the request
class PostBase(BaseModel):
    title:str
    content:str
    published:bool=True

class PostCreate(PostBase):
    pass


class UserResponse(BaseModel):
    id:int
    email: EmailStr
    created_at:datetime

    class Config:
        orm_mode = True

class PostResponse(PostBase):
    id: int
    created_at:datetime
    owner_id:int
    owner: UserResponse

    class Config:
        orm_mode = True

class PostResponseOut(BaseModel):
    Post:PostResponse
    votes:int

    class Config:
        orm_mode = True

class UserCreate(BaseModel):
    email: EmailStr
    password: str



class UserLogin(BaseModel):
    email: EmailStr
    password:str

class Token(BaseModel):
    access_token:str
    token_type:str

class TokenData(BaseModel):
    id: Optional[str]=None

class Vote(BaseModel):
    post_id:int 
    dir: int

    @validator('dir')
    def must_be_one_or_zero(cls,v):
        if v not in (0,1):
            raise ValueError('Must be either 1 or 0')
        return v