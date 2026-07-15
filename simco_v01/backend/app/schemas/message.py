from datetime import datetime
from pydantic import BaseModel

class MessageCreate(BaseModel):
    receiver_id: int | None = None
    content: str
    is_general: bool = False

class MessageOut(BaseModel):
    id: int
    sender_id: int
    sender_name: str | None = None
    receiver_id: int | None = None
    receiver_name: str | None = None
    content: str
    is_general: bool
    created_at: datetime
    read_at: datetime | None = None

    class Config:
        from_attributes = True

class UnreadCountOut(BaseModel):
    total: int

class UserMessageOut(BaseModel):
    id: int
    username: str
    full_name: str | None = None
    role: str
