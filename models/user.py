# models/user.py

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
import uuid

class LLMConfig(BaseModel):
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    model_id: Optional[str] = None

class User(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), alias="_id")
    username: str
    access_key: str = Field(unique=True)
    is_active: bool = True
    api_calls_total: int = 0
    api_call_limit: Optional[int] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    expires_on: Optional[datetime] = None
    
    device_key: Optional[str] = None
    
    txl_config: LLMConfig = Field(default_factory=LLMConfig)
    ixl_config: LLMConfig = Field(default_factory=LLMConfig)

class UserUpdate(BaseModel):
    username: Optional[str] = None
    is_active: Optional[bool] = None
    api_call_limit: Optional[int] = None
    expires_on: Optional[datetime] = None
    txl_config: Optional[LLMConfig] = None
    ixl_config: Optional[LLMConfig] = None