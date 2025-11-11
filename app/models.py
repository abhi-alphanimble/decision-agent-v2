# app/models.py
from sqlalchemy import (
    Column, Integer, String, Text, DateTime, Boolean, ForeignKey, Enum
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database.base import Base
import enum

class DecisionStatus(enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"

class VoteType(enum.Enum):
    APPROVE = "approve"
    REJECT = "reject"

class Decision(Base):
    __tablename__ = "decisions"

    id = Column(Integer, primary_key=True, index=True)
    text = Column(Text, nullable=False)
    status = Column(Enum(DecisionStatus), default=DecisionStatus.PENDING)
    proposer_phone = Column(String, nullable=True)
    proposer_name = Column(String, nullable=True)
    channel_id = Column(String, nullable=False, index=True)
    group_size_at_creation = Column(Integer, nullable=False)
    approval_threshold = Column(Integer, nullable=False)
    approval_count = Column(Integer, default=0)
    rejection_count = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    closed_at = Column(DateTime(timezone=True), nullable=True)

    # Relationship to votes
    votes = relationship("Vote", back_populates="decision", cascade="all, delete-orphan")

    def __repr__(self):
        return (
            f"<Decision(id={self.id}, text='{self.text[:25]}...', "
            f"status={self.status.value})>"
        )

class Vote(Base):
    __tablename__ = "votes"

    id = Column(Integer, primary_key=True, index=True)
    decision_id = Column(Integer, ForeignKey("decisions.id", ondelete="CASCADE"), nullable=False)
    voter_phone = Column(String, nullable=True)
    voter_name = Column(String, nullable=True)
    vote_type = Column(Enum(VoteType), nullable=False)
    is_anonymous = Column(Boolean, default=False)
    voted_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationship to decision
    decision = relationship("Decision", back_populates="votes")

    # Unique constraint to ensure one vote per user per decision
    __table_args__ = (
        {'schema': None} # Add this if you have a default schema
    )
    __mapper_args__ = {
        "confirm_deleted_rows": False
    }

    def __repr__(self):
        return (
            f"<Vote(id={self.id}, decision_id={self.decision_id}, "
            f"vote_type={self.vote_type.value})>"
        )

# Add the unique constraint after the class definition
from sqlalchemy import UniqueConstraint
Vote.__table_args__ = (
    UniqueConstraint('decision_id', 'voter_phone', name='uq_decision_voter'),
)
s