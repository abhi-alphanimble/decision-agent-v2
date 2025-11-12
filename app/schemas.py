
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, Literal

# Base response schemas
class HealthResponse(BaseModel):
    status: Literal["healthy", "unhealthy"]
    timestamp: datetime
    database: Literal["connected", "disconnected"]

class RootResponse(BaseModel):
    message: str
    version: str
    docs: str

class StatusResponse(BaseModel):
    api_version: str
    server_time: datetime
    database_status: Literal["connected", "disconnected"]
    total_decisions: int
    total_votes: int

class ErrorResponse(BaseModel):
    error: str
    detail: Optional[str] = None
    timestamp: datetime

# Decision schemas
class DecisionBase(BaseModel):
    text: str = Field(..., min_length=1, max_length=500)
    proposer_phone: str
    proposer_name: str
    channel_id: str
    group_size_at_creation: int = Field(..., gt=0)
    approval_threshold: int = Field(..., gt=0)

class DecisionCreate(DecisionBase):
    pass

class DecisionResponse(DecisionBase):
    id: int
    status: str
    approval_count: int
    rejection_count: int
    created_at: datetime
    closed_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# Vote schemas
class VoteBase(BaseModel):
    voter_phone: str
    voter_name: str
    vote_type: Literal["approve", "reject"]
    is_anonymous: bool = False

class VoteCreate(VoteBase):
    decision_id: int

class VoteResponse(VoteBase):
    id: int
    decision_id: int
    voted_at: datetime

    class Config:
        from_attributes = True


