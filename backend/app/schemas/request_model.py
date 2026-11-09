from pydantic import BaseModel, Field
from typing import Optional


class FAQRequest(BaseModel):
    """
    Request model for Healthcare FAQ Chatbot
    """

    question: str = Field(
        ...,
        min_length=3,
        max_length=1000,
        description="Healthcare question from user"
    )

    session_id: str = Field(
        ...,
        description="Unique conversation session ID"
    )

    user_id: Optional[str] = Field(
        default=None,
        description="User identifier"
    )

    language: Optional[str] = Field(
        default="English",
        description="Preferred response language"
    )

    conversation_id: Optional[str] = Field(
        default=None,
        description="Conversation tracking ID"
    )