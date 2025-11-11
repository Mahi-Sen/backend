# models/user.py (FINAL, CORRECTED VERSION)
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime
import uuid
from bson import ObjectId # Import this

# This is a helper class to handle MongoDB's ObjectId
class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate
    @classmethod
    def validate(cls, v, *args, **kwargs):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return ObjectId(v)
    @classmethod
    def __get_pydantic_json_schema__(cls, field_schema):
        field_schema.update(type="string")

class LLMConfig(BaseModel):
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    model_id: Optional[str] = None

class User(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    username: str
    access_key: str
    is_active: bool = True
    api_calls_total: int = 0
    api_call_limit: Optional[int] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    expires_on: Optional[datetime] = None
    device_key: Optional[str] = None
    txl_config: LLMConfig = Field(default_factory=LLMConfig)
    ixl_config: LLMConfig = Field(default_factory=LLMConfig)
    
    # New fields from admin.py logic
    pending_notification: Optional[str] = None
    uninstall_pending: Optional[bool] = False

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str} # This is key for sending response
    )

class UserUpdate(BaseModel):
    username: Optional[str] = None
    is_active: Optional[bool] = None
    api_call_limit: Optional[int] = None
    expires_on: Optional[datetime] = None
    txl_config: Optional[LLMConfig] = None
    ixl_config: Optional[LLMConfig] = None
    # Add other fields if you want to update them
