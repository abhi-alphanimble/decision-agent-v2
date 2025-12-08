
# app/models.py
from datetime import datetime, UTC

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Column,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship

from database.base import Base


class Decision(Base):
    __tablename__ = "decisions"

    id = Column(Integer, primary_key=True, index=True)
    text = Column(String, nullable=False)
    status = Column(String, nullable=False, default="pending")
    proposer_phone = Column(String, nullable=False, index=True)
    proposer_name = Column(String, nullable=False)
    channel_id = Column(String, nullable=False, index=True)
    group_size_at_creation = Column(Integer, nullable=False)
    approval_threshold = Column(Integer, nullable=False)
    approval_count = Column(Integer, default=0, nullable=False)
    rejection_count = Column(Integer, default=0, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(UTC), nullable=False)
    closed_at = Column(DateTime, nullable=True)

    votes = relationship("Vote", back_populates="decision", cascade="all, delete-orphan")

    __table_args__ = (
        CheckConstraint("approval_count >= 0", name="check_approval_count_positive"),
        CheckConstraint("rejection_count >= 0", name="check_rejection_count_positive"),
        CheckConstraint("group_size_at_creation > 0", name="check_group_size_positive"),
        CheckConstraint("approval_threshold > 0", name="check_threshold_positive"),
        CheckConstraint("status IN ('pending', 'approved', 'rejected', 'expired')", name="check_valid_status"),
    )

    @property
    def created_by(self) -> str:
        return self.proposer_phone

    @created_by.setter
    def created_by(self, value: str) -> None:
        self.proposer_phone = value

    @property
    def created_by_name(self) -> str:
        return self.proposer_name

    @created_by_name.setter
    def created_by_name(self, value: str) -> None:
        self.proposer_name = value

    def __repr__(self) -> str:
        return (
            f"<Decision(id={self.id}, text='{self.text[:30]}...', status='{self.status}', "
            f"approvals={self.approval_count}, rejections={self.rejection_count})>"
        )


class Vote(Base):
    __tablename__ = "votes"

    id = Column(Integer, primary_key=True, index=True)
    decision_id = Column(Integer, ForeignKey("decisions.id", ondelete="CASCADE"), nullable=False, index=True)
    voter_phone = Column(String, nullable=False, index=True)
    voter_name = Column(String, nullable=False)
    vote_type = Column(String, nullable=False)
    is_anonymous = Column(Boolean, default=False, nullable=False)
    voted_at = Column(DateTime, default=lambda: datetime.now(UTC), nullable=False)

    decision = relationship("Decision", back_populates="votes")

    __table_args__ = (
        UniqueConstraint("decision_id", "voter_phone", name="unique_voter_per_decision"),
        CheckConstraint("vote_type IN ('approve', 'reject')", name="check_valid_vote_type"),
        # Compound index for fast vote lookups by decision + voter
        Index("ix_votes_decision_voter", "decision_id", "voter_phone"),
    )

    @property
    def voter_id(self) -> str:
        return self.voter_phone

    @voter_id.setter
    def voter_id(self, value: str) -> None:
        self.voter_phone = value

    def __repr__(self) -> str:
        return (
            f"<Vote(id={self.id}, decision_id={self.decision_id}, voter='{self.voter_name}', "
            f"vote_type='{self.vote_type}', anonymous={self.is_anonymous})>"
        )

    @property
    def vote(self) -> str:
        return self.vote_type

    @vote.setter
    def vote(self, value: str) -> None:
        self.vote_type = value


class SlackInstallation(Base):
    __tablename__ = "slack_installations"

    team_id = Column(String, primary_key=True, index=True)
    team_name = Column(String, nullable=True)
    access_token = Column(String, nullable=False)
    bot_user_id = Column(String, nullable=False)
    installed_at = Column(DateTime, default=lambda: datetime.now(UTC), nullable=False)

    def __repr__(self) -> str:
        return f"<SlackInstallation(team_id={self.team_id}, team_name='{self.team_name}')>"


class ChannelConfig(Base):
    __tablename__ = "channel_configs"

    channel_id = Column(String, primary_key=True, index=True)
    approval_percentage = Column(Integer, nullable=False, default=60)  # Stored as integer (60 = 60%)
    auto_close_hours = Column(Integer, nullable=False, default=48)
    updated_at = Column(DateTime, default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC), nullable=False)
    updated_by = Column(String, nullable=True)  # User ID who last updated

    __table_args__ = (
        CheckConstraint("approval_percentage > 0 AND approval_percentage <= 100", name="check_valid_percentage"),
        CheckConstraint("auto_close_hours > 0", name="check_valid_hours"),
    )

    def __repr__(self) -> str:
        return (
            f"<ChannelConfig(channel_id={self.channel_id}, "
            f"approval={self.approval_percentage}%, hours={self.auto_close_hours})>"
        )


class ConfigChangeLog(Base):
    __tablename__ = "config_change_logs"

    id = Column(Integer, primary_key=True, index=True)
    channel_id = Column(String, nullable=False, index=True)
    setting_name = Column(String, nullable=False)  # approval_percentage, auto_close_hours, group_size
    old_value = Column(Integer, nullable=False)
    new_value = Column(Integer, nullable=False)
    changed_by = Column(String, nullable=False)  # User ID
    changed_by_name = Column(String, nullable=False)  # Username for display
    changed_at = Column(DateTime, default=lambda: datetime.now(UTC), nullable=False)

    __table_args__ = (
        CheckConstraint("setting_name IN ('approval_percentage', 'auto_close_hours')", name="check_valid_setting_name"),
    )

    def __repr__(self) -> str:
        return (
            f"<ConfigChangeLog(id={self.id}, channel={self.channel_id}, "
            f"setting={self.setting_name}, {self.old_value}→{self.new_value}, by={self.changed_by_name})>"
        )

