"""
Database models for AfroKen using SQLModel.

Each class here corresponds to a database table with columns defined by the
type-annotated attributes.
"""

from typing import Optional
from sqlmodel import SQLModel, Field
from datetime import datetime
import uuid


class User(SQLModel, table=True):
    """
    Represents an end user interacting with AfroKen.

    `table=True` tells SQLModel to create a physical table for this model.
    """

    # Primary key stored as a stringified UUID, generated automatically.
    id: Optional[str] = Field(
        default_factory=lambda: str(uuid.uuid4()), primary_key=True
    )
    # Phone number uniquely identifies a user and is indexed for fast lookups.
    phone_number: str = Field(index=True, nullable=False, unique=True)
    # Optional email address for the user.
    email: Optional[str] = None
    # User's preferred language code (Swahili by default).
    preferred_language: str = Field(default="sw")
    # Soft-delete flag or activation flag for the account.
    is_active: bool = Field(default=True)
    # Timestamp indicating when the user record was created.
    created_at: datetime = Field(default_factory=datetime.utcnow)


class Conversation(SQLModel, table=True):
    """
    Represents a logical conversation thread between a user and AfroKen.
    """

    # Primary key as a UUID string, generated automatically.
    id: Optional[str] = Field(
        default_factory=lambda: str(uuid.uuid4()), primary_key=True
    )
    # Foreign key referencing the owning user in the `user` table.
    user_id: str = Field(foreign_key="user.id")
    # High-level category of the service (e.g. "NHIF", "KRA", "Business").
    service_category: Optional[str] = None
    # Conversation status (e.g. active, closed, pending).
    status: str = Field(default="active")
    # Optional short summary of the conversation for analytics or search.
    summary: Optional[str] = None
    # Optional sentiment label (e.g. positive, neutral, negative).
    sentiment: Optional[str] = None
    # Creation timestamp for when the conversation started.
    created_at: datetime = Field(default_factory=datetime.utcnow)


class Message(SQLModel, table=True):
    """
    Individual message within a conversation.

    Can represent either user messages or AI responses based on the `role` field.
    """

    # Primary key as a UUID string, generated automatically.
    id: Optional[str] = Field(
        default_factory=lambda: str(uuid.uuid4()), primary_key=True
    )
    # Foreign key referencing the conversation to which this message belongs.
    conversation_id: str = Field(foreign_key="conversation.id")
    # Role of the sender, e.g. "user" or "assistant".
    role: str = Field(default="user")
    # Raw message content text.
    content: str
    # Optional language code if detected or specified.
    language: Optional[str] = None
    # Optional JSON-encoded string of citations or source references.
    citations: Optional[str] = None  # JSON text
    # Number of tokens consumed to generate this message (if tracked).
    tokens_used: Optional[int] = 0
    # Approximate cost in USD for generating this message (if tracked).
    cost_usd: Optional[float] = 0.0
    # Timestamp indicating when the message was created.
    created_at: datetime = Field(default_factory=datetime.utcnow)


class Document(SQLModel, table=True):
    """
    Ingested content document that can be searched via embeddings.
    """

    # Primary key as a UUID string, generated automatically.
    id: Optional[str] = Field(
        default_factory=lambda: str(uuid.uuid4()), primary_key=True
    )
    # Human-friendly document title or filename.
    title: str
    # Raw text content (or extracted text) of the document.
    content: str
    # URL pointing to where the document is stored (e.g. MinIO location).
    source_url: Optional[str] = None
    # Optional document type label (e.g. "pdf", "policy", "form").
    document_type: Optional[str] = None
    # Optional business/category label for filtering (e.g. "NHIF", "KRA").
    category: Optional[str] = None
    # Flag indicating whether this document has had its embedding computed & stored.
    is_indexed: bool = Field(default=False)
    # Timestamp indicating when the document record was created.
    created_at: datetime = Field(default_factory=datetime.utcnow)

