from pydantic import BaseModel
from typing import Optional, List


class TokenRequest(BaseModel):
    phone_number: str


class TokenVerify(BaseModel):
    phone_number: str
    code: str


class ChatRequest(BaseModel):
    conversation_id: Optional[str]
    message: str
    device: Optional[str] = "web"
    language: Optional[str] = "sw"


class ChatResponse(BaseModel):
    reply: str
    citations: Optional[List[str]] = []


class DocumentIn(BaseModel):
    title: str
    content: str
    source_url: Optional[str] = None
    document_type: Optional[str] = None
    category: Optional[str] = None



