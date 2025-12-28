
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
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship

from database.base import Base


class ZohoInstallation(Base):
    """
    Primary organization table - Zoho CRM connection is required first.
    Uses zoho_org_id as the organization identifier.
    """
    __tablename__ = "zoho_installations"

    id = Column(Integer, primary_key=True, index=True)
    zoho_org_id = Column(String(100), unique=True, nullable=False, index=True)  # Primary org identifier
    zoho_domain = Column(String(50), nullable=False)  # e.g., 'com', 'in', 'eu'
    access_token = Column(Text, nullable=False)  # Encrypted
    refresh_token = Column(Text, nullable=False)  # Encrypted
    token_expires_at = Column(DateTime, nullable=True)
    installed_at = Column(DateTime, default=lambda: datetime.now(UTC), nullable=False)
    installed_by = Column(String(100), nullable=True)  # User who connected

    # Relationships
    slack_installation = relationship("SlackInstallation", back_populates="zoho_installation", uselist=False, cascade="all, delete-orphan")
    decisions = relationship("Decision", back_populates="zoho_installation", cascade="all, delete-orphan")
    ai_limits = relationship("OrganizationAILimits", back_populates="zoho_installation", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return (
            f"<ZohoInstallation(id={self.id}, zoho_org_id={self.zoho_org_id}, "
            f"domain={self.zoho_domain})>"
        )


class SlackInstallation(Base):
    """Slack workspace installation - linked to Zoho organization."""
    __tablename__ = "slack_installations"

    team_id = Column(String, primary_key=True, index=True)
    team_name = Column(String, nullable=True)
    access_token = Column(String, nullable=False)
    bot_user_id = Column(String, nullable=False)
    installed_at = Column(DateTime, default=lambda: datetime.now(UTC), nullable=False)
    zoho_org_id = Column(String(100), ForeignKey("zoho_installations.zoho_org_id", ondelete="CASCADE"), nullable=False, index=True)

    # Relationship back to Zoho
    zoho_installation = relationship("ZohoInstallation", back_populates="slack_installation")

    def __repr__(self) -> str:
        return f"<SlackInstallation(team_id={self.team_id}, team_name='{self.team_name}', zoho_org_id='{self.zoho_org_id}')>"


class Decision(Base):
    __tablename__ = "decisions"

    id = Column(Integer, primary_key=True, index=True)
    text = Column(String, nullable=False)
    status = Column(String, nullable=False, default="pending")
    proposer_phone = Column(String, nullable=False, index=True)
    proposer_name = Column(String, nullable=False)
    channel_id = Column(String, nullable=False, index=True)
    team_id = Column(String, nullable=True, index=True)  # Slack team ID for reference
    zoho_org_id = Column(String(100), ForeignKey("zoho_installations.zoho_org_id", ondelete="CASCADE"), nullable=False, index=True)
    group_size_at_creation = Column(Integer, nullable=False)
    approval_threshold = Column(Integer, nullable=False)
    approval_count = Column(Integer, default=0, nullable=False)
    rejection_count = Column(Integer, default=0, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(UTC), nullable=False)
    closed_at = Column(DateTime, nullable=True)
    zoho_synced = Column(Boolean, default=False, nullable=False)  # Track if synced to Zoho CRM

    votes = relationship("Vote", back_populates="decision", cascade="all, delete-orphan")
    zoho_installation = relationship("ZohoInstallation", back_populates="decisions")

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
            f"vote_type='{self.vote_type}')>"
        )

    @property
    def vote(self) -> str:
        return self.vote_type

    @vote.setter
    def vote(self, value: str) -> None:
        self.vote_type = value


class ChannelConfig(Base):
    __tablename__ = "channel_configs"

    channel_id = Column(String, primary_key=True, index=True)
    approval_percentage = Column(Integer, nullable=False, default=60)  # Stored as integer (60 = 60%)
    updated_at = Column(DateTime, default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC), nullable=False)
    updated_by = Column(String, nullable=True)  # User ID who last updated

    __table_args__ = (
        CheckConstraint("approval_percentage > 0 AND approval_percentage <= 100", name="check_valid_percentage"),
    )

    def __repr__(self) -> str:
        return (
            f"<ChannelConfig(channel_id={self.channel_id}, "
            f"approval={self.approval_percentage}%)>"
        )


class ConfigChangeLog(Base):
    __tablename__ = "config_change_logs"

    id = Column(Integer, primary_key=True, index=True)
    channel_id = Column(String, nullable=False, index=True)
    setting_name = Column(String, nullable=False)  # approval_percentage
    old_value = Column(Integer, nullable=False)
    new_value = Column(Integer, nullable=False)
    changed_by = Column(String, nullable=False)  # User ID
    changed_by_name = Column(String, nullable=False)  # Username for display
    changed_at = Column(DateTime, default=lambda: datetime.now(UTC), nullable=False)

    __table_args__ = (
        CheckConstraint("setting_name = 'approval_percentage'", name="check_valid_setting_name"),
    )

    def __repr__(self) -> str:
        return (
            f"<ConfigChangeLog(id={self.id}, channel={self.channel_id}, "
            f"setting={self.setting_name}, {self.old_value}→{self.new_value}, by={self.changed_by_name})>"
        )


class OrganizationAILimits(Base):
    """
    Consolidated table for AI usage limits per organization.
    Combines config (monthly_limit) and usage tracking (command_count) in one table.
    Uses month_year for automatic monthly reset - new month = new record with count=0.
    """
    __tablename__ = "organization_ai_limits"

    id = Column(Integer, primary_key=True, index=True)
    zoho_org_id = Column(String(100), ForeignKey("zoho_installations.zoho_org_id", ondelete="CASCADE"), nullable=False, index=True)
    month_year = Column(String(7), nullable=False, index=True)  # Format: "YYYY-MM" (e.g., "2025-12")
    monthly_limit = Column(Integer, nullable=False, default=100)  # Default 100 AI commands per month
    command_count = Column(Integer, nullable=False, default=0)
    last_used_at = Column(DateTime, default=lambda: datetime.now(UTC), nullable=False)

    # Relationship
    zoho_installation = relationship("ZohoInstallation", back_populates="ai_limits")

    __table_args__ = (
        UniqueConstraint("zoho_org_id", "month_year", name="unique_org_month_limits"),
        CheckConstraint("monthly_limit > 0", name="check_monthly_limit_positive"),
        CheckConstraint("command_count >= 0", name="check_command_count_non_negative"),
        Index("ix_ai_limits_org_month", "zoho_org_id", "month_year"),
    )

    def __repr__(self) -> str:
        return (
            f"<OrganizationAILimits(id={self.id}, zoho_org_id={self.zoho_org_id}, "
            f"month={self.month_year}, limit={self.monthly_limit}, count={self.command_count})>"
        )
