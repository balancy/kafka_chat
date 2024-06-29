"""Models for the application."""

from pydantic import BaseModel


class Message(BaseModel):
    """Model for a message."""

    username: str
    content: str
