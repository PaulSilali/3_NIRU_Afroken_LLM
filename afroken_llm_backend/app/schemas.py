"""
Pydantic request/response schemas for the AfroKen API.

These classes define the shape of JSON payloads accepted by and returned from
FastAPI endpoints. FastAPI uses them for validation and OpenAPI docs.
"""

from pydantic import BaseModel
from typing import Optional, List


class TokenRequest(BaseModel):
    """
    Request body for asking the backend to send an OTP to a phone number.
    """

    # MSISDN (phone number) the OTP should be associated with.
    phone_number: str


class TokenVerify(BaseModel):
    """
    Request body for verifying an OTP that was sent earlier.
    """

    # The same phone number that requested the OTP.
    phone_number: str
    # One-time password code entered by the user.
    code: str


class ChatRequest(BaseModel):
    """
    Request payload for sending a chat message to AfroKen.
    """

    # Optional conversation identifier so the backend can thread context;
    # if omitted, a new conversation can be created.
    conversation_id: Optional[str]
    # The natural language message from the end user.
    message: str
    # Optional device label (e.g. "web", "ussd", "sms") for analytics.
    device: Optional[str] = "web"
    # Preferred reply language code; defaults to Swahili ("sw").
    language: Optional[str] = "sw"


class ChatResponse(BaseModel):
    """
    Response payload returned by the chat endpoint.
    """

    # The model's reply text to show to the user.
    reply: str
    # List of citation identifiers/URLs/titles that support the answer.
    citations: Optional[List[str]] = []


class DocumentIn(BaseModel):
    """
    Schema for creating a new document record programmatically (not via file upload).
    """

    # Human-readable title for the document.
    title: str
    # Raw text content of the document.
    content: str
    # Optional URL or storage path indicating where the document lives.
    source_url: Optional[str] = None
    # Optional type label (e.g. "pdf", "policy").
    document_type: Optional[str] = None
    # Optional category label for grouping/searching (e.g. "NHIF").
    category: Optional[str] = None

