import uuid
from datetime import datetime, timezone
from enum import Enum

from sqlalchemy import DateTime
from sqlmodel import Field, Relationship, SQLModel


def get_datetime_utc() -> datetime:
    return datetime.now(timezone.utc)


class TeamRole(str, Enum):
    ENGINEER = "ENGINEER"
    RESEARCHER = "RESEARCHER"
    OPERATOR = "OPERATOR"
    IP_MANAGER = "IP_MANAGER"


# Shared properties
class TeamBase(SQLModel):
    name: str = Field(unique=True, index=True, max_length=255)
    description: str | None = Field(default=None, max_length=1024)


# Properties to receive via API on creation
class TeamCreate(TeamBase):
    pass


# Properties to receive via API on update, all are optional
class TeamUpdate(SQLModel):
    name: str | None = Field(default=None, max_length=255)
    description: str | None = Field(default=None, max_length=1024)


# Database model, database table inferred from class name
class Team(TeamBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    created_at: datetime | None = Field(
        default_factory=get_datetime_utc,
        sa_type=DateTime(timezone=True),  # type: ignore
    )

    memberships: list["TeamMembership"] = Relationship(
        back_populates="team",
        cascade_delete=True,
    )


# Properties to return via API, id is always required
class TeamPublic(TeamBase):
    id: uuid.UUID
    created_at: datetime | None = None


class TeamsPublic(SQLModel):
    data: list[TeamPublic]
    count: int


# Shared properties
class TeamMembershipBase(SQLModel):
    role: TeamRole = Field(default=TeamRole.ENGINEER)


# Properties to receive via API on creation
class TeamMembershipCreate(TeamMembershipBase):
    user_id: uuid.UUID
    team_id: uuid.UUID


# Database model
class TeamMembership(TeamMembershipBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)

    user_id: uuid.UUID = Field(
        foreign_key="user.id",
        nullable=False,
        ondelete="CASCADE",
    )
    team_id: uuid.UUID = Field(
        foreign_key="team.id",
        nullable=False,
        ondelete="CASCADE",
    )

    team: Team | None = Relationship(back_populates="memberships")


# Properties to return via API
class TeamMembershipPublic(TeamMembershipBase):
    id: uuid.UUID
    user_id: uuid.UUID
    team_id: uuid.UUID