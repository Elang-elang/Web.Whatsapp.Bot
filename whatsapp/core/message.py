from dataclasses import dataclass
from typing import Option, List, Dict, Any
from datetime import datetime

@dataclass
class Message:
    body: Option[str] = None
    type: str = "text"

@dataclass
class SourceMessage:
    sender: str
    chat: str
    id: str

@dataclass
class InfoMessage:
    source: SourceMessage
    name: str
    is_from_me: Option[bool]
    timestamp: datetime