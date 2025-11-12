from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, CheckConstraint, UniqueConstraint
from sqlalchemy.orm import relationship
from datetime import datetime
from database.base import Base

class Decision(Base):
    __tablename__ = 'decisions'
    
    id = Column(Integer, primary_key=True, index=True)
    text = Column(String, nullable=False)
    status = Column(String, nullable=False, default='pending')  # pending, approved, rejected, expired
    proposer_phone = Column(String, nullable=False, index=True)
    proposer_name = Column(String, nullable=False)
    channel_id = Column(String, nullable=False, index=True)
    group_size_at_creation = Column(Integer, nullable=False)
    approval_threshold = Column(Integer, nullable=False)
    approval_count = Column(Integer, default=0, nullable=False)
    rejection_count = Column(Integer, default=0, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    closed_at = Column(DateTime, nullable=True)
    
    # Relationship to votes
    votes = relationship("Vote", back_populates="decision", cascade="all, delete-orphan")
    
    # Constraints
    __table_args__ = (
        CheckConstraint('approval_count >= 0', name='check_approval_count_positive'),
        CheckConstraint('rejection_count >= 0', name='check_rejection_count_positive'),
        CheckConstraint('group_size_at_creation > 0', name='check_group_size_positive'),
        CheckConstraint('approval_threshold > 0', name='check_threshold_positive'),
        CheckConstraint("status IN ('pending', 'approved', 'rejected', 'expired')", name='check_valid_status'),
    )
    
    def __repr__(self):
        return f"<Decision(id={self.id}, text='{self.text[:30]}...', status='{self.status}', " \
               f"approvals={self.approval_count}, rejections={self.rejection_count})>"


class Vote(Base):
    __tablename__ = 'votes'
    
    id = Column(Integer, primary_key=True, index=True)
    decision_id = Column(Integer, ForeignKey('decisions.id', ondelete='CASCADE'), nullable=False, index=True)
    voter_phone = Column(String, nullable=False, index=True)
    voter_name = Column(String, nullable=False)
    vote_type = Column(String, nullable=False)  # approve, reject
    is_anonymous = Column(Boolean, default=False, nullable=False)
    voted_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationship to decision
    decision = relationship("Decision", back_populates="votes")
    
    # Constraints
    __table_args__ = (
        UniqueConstraint('decision_id', 'voter_phone', name='unique_voter_per_decision'),
        CheckConstraint("vote_type IN ('approve', 'reject')", name='check_valid_vote_type'),
    )
    
    def __repr__(self):
        return f"<Vote(id={self.id}, decision_id={self.decision_id}, voter='{self.voter_name}', " \
               f"vote_type='{self.vote_type}', anonymous={self.is_anonymous})>"
