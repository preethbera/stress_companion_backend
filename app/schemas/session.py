from pydantic import BaseModel
from typing import Optional
import uuid
from datetime import datetime

# --- Session Schemas ---
class SessionCreateResponse(BaseModel):
    session_id: uuid.UUID
    status: str
    created_at: datetime

    class Config:
        from_attributes = True

class SessionUpdateRequest(BaseModel):
    status: str  # e.g. 'completed'

# --- Frame Schemas ---
# (Frames are now processed exclusively via WebSockets; no REST payload needed)

# --- Message Schemas ---
class MessageCreateRequest(BaseModel):
    session_id: uuid.UUID
    role: str  # 'user' or 'assistant'
    content: str

class MessageResponse(BaseModel):
    message_id: int
    session_id: uuid.UUID
    role: str
    content: str
    timestamp: Optional[datetime] = None

    class Config:
        from_attributes = True

class SessionHistoryItem(BaseModel):
    session_id: uuid.UUID
    created_at: datetime
    status: str
    avg_optical_stress: Optional[float] = None
    avg_thermal_stress: Optional[float] = None

class TimelinePoint(BaseModel):
    timestamp: int # Date.now() representation or timestamp string
    score: Optional[float] = None
    prob: Optional[float] = None
    status: str

class SessionDetailResponse(BaseModel):
    session_id: uuid.UUID
    created_at: datetime
    optical: list[TimelinePoint]
    thermal: list[TimelinePoint]
    messages: list[MessageResponse]
