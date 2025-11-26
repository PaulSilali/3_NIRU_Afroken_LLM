from typing import Optional
from sqlmodel import SQLModel, Field
from datetime import datetime
import uuid


class User(SQLModel, table=True):
    id: Optional[str] = Field(
        default_factory=lambda: str(uuid.uuid4()), primary_key=True
    )
    phone_number: str = Field(index=True, nullable=False, unique=True)
    email: Optional[str] = None
    preferred_language: str = Field(default="sw")
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class Conversation(SQLModel, table=True):
    id: Optional[str] = Field(
        default_factory=lambda: str(uuid.uuid4()), primary_key=True
    )
    user_id: str = Field(foreign_key="user.id")
    service_category: Optional[str] = None
    status: str = Field(default="active")
    summary: Optional[str] = None
    sentiment: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)


class Message(SQLModel, table=True):
    id: Optional[str] = Field(
        default_factory=lambda: str(uuid.uuid4()), primary_key=True
    )
    conversation_id: str = Field(foreign_key="conversation.id")
    role: str = Field(default="user")
    content: str
    language: Optional[str] = None
    citations: Optional[str] = None  # JSON text
    tokens_used: Optional[int] = 0
    cost_usd: Optional[float] = 0.0
    created_at: datetime = Field(default_factory=datetime.utcnow)


class Document(SQLModel, table=True):
    id: Optional[str] = Field(
        default_factory=lambda: str(uuid.uuid4()), primary_key=True
    )
    title: str
    content: str
    source_url: Optional[str] = None
    document_type: Optional[str] = None
    category: Optional[str] = None
    is_indexed: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)



