from sqlalchemy import Column, String, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
import uuid

from src.core.database import Base


def generate_uuid():
    return str(uuid.uuid4())


class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=generate_uuid)
    email = Column(String, unique=True, index=True)
    full_name = Column(String)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    teams = relationship("TeamMembership", back_populates="user")


class Team(Base):
    __tablename__ = "teams"

    id = Column(String, primary_key=True, default=generate_uuid)
    name = Column(String, unique=True, index=True)
    description = Column(String, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    members = relationship("TeamMembership", back_populates="team")
    projects = relationship("ProjectDB", back_populates="team")


class TeamMembership(Base):
    __tablename__ = "team_memberships"

    user_id = Column(String, ForeignKey("users.id"), primary_key=True)
    team_id = Column(String, ForeignKey("teams.id"), primary_key=True)
    role = Column(String, default="member")  # "admin" or "member"

    user = relationship("User", back_populates="teams")
    team = relationship("Team", back_populates="members")


class ProjectDB(Base):
    __tablename__ = "projects"

    id = Column(String, primary_key=True, default=generate_uuid)
    name = Column(String, index=True)
    description = Column(String, nullable=True)
    team_id = Column(String, ForeignKey("teams.id"), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    team = relationship("Team", back_populates="projects")


class StandardSource(Base):
    __tablename__ = "standard_sources"

    id = Column(String, primary_key=True, default=generate_uuid)
    name = Column(String, index=True)
    url = Column(String)
    last_synced_at = Column(DateTime, nullable=True)
    sync_interval_hours = Column(String, default="24")

    rules = relationship("RuleDefinition", back_populates="source")


class RuleDefinition(Base):
    __tablename__ = "rules"

    id = Column(String, primary_key=True)
    source_id = Column(String, ForeignKey("standard_sources.id"))
    language = Column(String)
    severity = Column(String)
    description = Column(String)
    ast_query = Column(String)
    remediation_effort_minutes = Column(String, default="15")
    is_active = Column(Boolean, default=True)
    version = Column(String, default="1.0.0")

    source = relationship("StandardSource", back_populates="rules")
    overrides = relationship("RuleOverride", back_populates="rule")


class RuleOverride(Base):
    __tablename__ = "rule_overrides"

    id = Column(String, primary_key=True, default=generate_uuid)
    rule_id = Column(String, ForeignKey("rules.id"))
    org_id = Column(String) # Placeholder for future Organization linking
    override_severity = Column(String, nullable=True)
    is_disabled = Column(Boolean, default=False)
    custom_message = Column(String, nullable=True)

    rule = relationship("RuleDefinition", back_populates="overrides")
