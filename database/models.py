# database/models.py
"""
Database models for multi-workspace Slack bot
"""
from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from database.base import Base


class Workspace(Base):
    """
    Stores information about each Slack workspace that installs the bot
    """
    __tablename__ = "workspaces"
    
    id = Column(Integer, primary_key=True, index=True)
    team_id = Column(String(50), unique=True, index=True, nullable=False)
    team_name = Column(String(255), nullable=False)
    bot_token = Column(Text, nullable=False)  # Store encrypted in production!
    bot_user_id = Column(String(50), nullable=False)
    installed_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    
    # Relationship to decisions
    decisions = relationship("Decision", back_populates="workspace")
    
    def __repr__(self):
        return f"<Workspace {self.team_name} ({self.team_id})>"


class Decision(Base):
    """
    Stores decision proposals (now linked to specific workspace)
    """
    __tablename__ = "decisions"
    
    id = Column(Integer, primary_key=True, index=True)
    text = Column(Text, nullable=False)
    proposer_id = Column(String(50), nullable=False)
    proposer_name = Column(String(255), nullable=False)
    channel_id = Column(String(50), nullable=False)
    
    # Link to workspace
    team_id = Column(String(50), ForeignKey("workspaces.team_id"), nullable=False)
    workspace = relationship("Workspace", back_populates="decisions")
    
    status = Column(String(20), default="pending")  # pending, approved, rejected
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Vote counts
    approval_count = Column(Integer, default=0)
    rejection_count = Column(Integer, default=0)
    
    # Relationships
    votes = relationship("Vote", back_populates="decision", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Decision {self.id}: {self.text[:50]}... ({self.status})>"


class Vote(Base):
    """
    Stores individual votes on decisions
    """
    __tablename__ = "votes"
    
    id = Column(Integer, primary_key=True, index=True)
    decision_id = Column(Integer, ForeignKey("decisions.id"), nullable=False)
    user_id = Column(String(50), nullable=False)
    user_name = Column(String(255), nullable=False)
    vote_type = Column(String(10), nullable=False)  # "approve" or "reject"
    is_anonymous = Column(Boolean, default=False)
    voted_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship
    decision = relationship("Decision", back_populates="votes")
    
    def __repr__(self):
        anon = " (anonymous)" if self.is_anonymous else ""
        return f"<Vote {self.user_name}: {self.vote_type}{anon}>"


# CRUD operations for workspaces
from sqlalchemy.orm import Session
from typing import Optional


def create_or_update_workspace(
    db: Session,
    team_id: str,
    team_name: str,
    bot_token: str,
    bot_user_id: str
) -> Workspace:
    """
    Create new workspace or update existing one
    """
    workspace = db.query(Workspace).filter(Workspace.team_id == team_id).first()
    
    if workspace:
        # Update existing
        workspace.team_name = team_name
        workspace.bot_token = bot_token
        workspace.bot_user_id = bot_user_id
        workspace.is_active = True
    else:
        # Create new
        workspace = Workspace(
            team_id=team_id,
            team_name=team_name,
            bot_token=bot_token,
            bot_user_id=bot_user_id
        )
        db.add(workspace)
    
    db.commit()
    db.refresh(workspace)
    return workspace


def get_workspace_by_team_id(db: Session, team_id: str) -> Optional[Workspace]:
    """Get workspace by team ID"""
    return db.query(Workspace).filter(
        Workspace.team_id == team_id,
        Workspace.is_active == True
    ).first()


def get_bot_token_for_team(db: Session, team_id: str) -> Optional[str]:
    """Get bot token for a specific workspace"""
    workspace = get_workspace_by_team_id(db, team_id)
    return workspace.bot_token if workspace else None