from typing import Optional

from pydantic import BaseModel, Field


class Voice(BaseModel):
    file_id: str
    mime_type: Optional[str] = None
    file_size: Optional[int] = None
    duration: Optional[int] = None


class Chat(BaseModel):
    id: int


class FromUser(BaseModel):
    id: int


class Message(BaseModel):
    message_id: int
    chat: Chat
    from_: FromUser = Field(alias="from")
    voice: Optional[Voice] = None


class Update(BaseModel):
    update_id: int
    message: Optional[Message] = None
