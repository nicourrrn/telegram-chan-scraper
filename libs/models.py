from pydantic import BaseModel


class Channel(BaseModel):
    name: str
    last_message_id: int


class ApiData(BaseModel):
    hash: str
    id: int


class DstChat(BaseModel):
    name: str
    username: str


class Config(BaseModel):
    filename: str
    channels: list[Channel]
    dst_chat: DstChat
