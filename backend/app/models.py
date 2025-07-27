import uuid
from datetime import datetime
from typing import Optional

from pydantic import EmailStr
from sqlmodel import Field, Relationship, SQLModel, Column, Text


# Link tables for many-to-many relationships
class TeamMember(SQLModel, table=True):
    __tablename__ = "team_member"
    
    team_id: uuid.UUID = Field(foreign_key="team.id", primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="user.id", primary_key=True)


class ShortlistIdea(SQLModel, table=True):
    __tablename__ = "shortlist_idea"
    
    shortlist_id: uuid.UUID = Field(foreign_key="shortlist.id", primary_key=True)
    idea_id: uuid.UUID = Field(foreign_key="idea.id", primary_key=True)


# Shared properties
class UserBase(SQLModel):
    email: EmailStr = Field(unique=True, index=True, max_length=255)
    is_active: bool = True
    is_superuser: bool = False
    full_name: Optional[str] = Field(default=None, max_length=255)


# Properties to receive via API on creation
class UserCreate(UserBase):
    password: str = Field(min_length=8, max_length=40)


class UserRegister(SQLModel):
    email: EmailStr = Field(max_length=255)
    password: str = Field(min_length=8, max_length=40)
    full_name: Optional[str] = Field(default=None, max_length=255)


# Properties to receive via API on update, all are optional
class UserUpdate(UserBase):
    email: Optional[EmailStr] = Field(default=None, max_length=255)  # type: ignore
    password: Optional[str] = Field(default=None, min_length=8, max_length=40)


class UserUpdateMe(SQLModel):
    full_name: Optional[str] = Field(default=None, max_length=255)
    email: Optional[EmailStr] = Field(default=None, max_length=255)


class UpdatePassword(SQLModel):
    current_password: str = Field(min_length=8, max_length=40)
    new_password: str = Field(min_length=8, max_length=40)


# Database model, database table inferred from class name
class User(UserBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    hashed_password: str
    items: list["Item"] = Relationship(back_populates="owner", cascade_delete=True)
    
    # New relationships
    profile: Optional["UserProfile"] = Relationship(back_populates="user", cascade_delete=True)
    resumes: list["UserResume"] = Relationship(back_populates="user", cascade_delete=True)
    repos: list["Repo"] = Relationship(back_populates="owner", cascade_delete=True)
    owned_teams: list["Team"] = Relationship(back_populates="owner", cascade_delete=True)
    teams: list["Team"] = Relationship(back_populates="members", link_model=TeamMember)
    ideas: list["Idea"] = Relationship(back_populates="creator", cascade_delete=True)
    shortlists: list["Shortlist"] = Relationship(back_populates="user", cascade_delete=True)
    deep_dive_versions: list["DeepDiveVersion"] = Relationship(back_populates="author", cascade_delete=True)
    case_studies: list["CaseStudy"] = Relationship(back_populates="author", cascade_delete=True)
    market_snapshots: list["MarketSnapshot"] = Relationship(back_populates="author", cascade_delete=True)
    lens_insights: list["LensInsight"] = Relationship(back_populates="author", cascade_delete=True)
    vc_thesis_comparisons: list["VCThesisComparison"] = Relationship(back_populates="author", cascade_delete=True)
    investor_decks: list["InvestorDeck"] = Relationship(back_populates="author", cascade_delete=True)
    idea_collaborations: list["IdeaCollaborator"] = Relationship(back_populates="user", cascade_delete=True, sa_relationship_kwargs={"foreign_keys": "[IdeaCollaborator.user_id]"})
    sent_idea_invitations: list["IdeaCollaborator"] = Relationship(back_populates="inviter", cascade_delete=True, sa_relationship_kwargs={"foreign_keys": "[IdeaCollaborator.invited_by]"})
    proposed_changes: list["IdeaChangeProposal"] = Relationship(back_populates="proposer", cascade_delete=True, sa_relationship_kwargs={"foreign_keys": "[IdeaChangeProposal.proposer_id]"})
    reviewed_changes: list["IdeaChangeProposal"] = Relationship(back_populates="reviewer", cascade_delete=True, sa_relationship_kwargs={"foreign_keys": "[IdeaChangeProposal.reviewer_id]"})
    comments: list["Comment"] = Relationship(back_populates="author", cascade_delete=True)
    sent_invites: list["Invite"] = Relationship(back_populates="inviter", cascade_delete=True)
    idea_qnas: list["IdeaVersionQnA"] = Relationship(back_populates="author", cascade_delete=True)
    audit_logs: list["AuditLog"] = Relationship(back_populates="user", cascade_delete=True)
    profile_qnas: list["ProfileQnA"] = Relationship(back_populates="user", cascade_delete=True)
    notifications: list["Notification"] = Relationship(back_populates="user", cascade_delete=True)
    export_records: list["ExportRecord"] = Relationship(back_populates="user", cascade_delete=True)
    iterations: list["Iteration"] = Relationship(back_populates="author", cascade_delete=True)
    suggestions: list["Suggested"] = Relationship(back_populates="user", cascade_delete=True)
    iterating_records: list["Iterating"] = Relationship(back_populates="user", cascade_delete=True)
    llm_input_logs: list["LLMInputLog"] = Relationship(back_populates="user", cascade_delete=True)


# Properties to return via API, id is always required
class UserPublic(UserBase):
    id: uuid.UUID


class UsersPublic(SQLModel):
    data: list[UserPublic]
    count: int


# Shared properties
class ItemBase(SQLModel):
    title: str = Field(min_length=1, max_length=255)
    description: Optional[str] = Field(default=None, max_length=255)


# Properties to receive on item creation
class ItemCreate(ItemBase):
    pass


# Properties to receive on item update
class ItemUpdate(ItemBase):
    title: Optional[str] = Field(default=None, min_length=1, max_length=255)  # type: ignore


# Database model, database table inferred from class name
class Item(ItemBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    owner_id: uuid.UUID = Field(
        foreign_key="user.id", nullable=False, ondelete="CASCADE"
    )
    owner: Optional[User] = Relationship(back_populates="items")


# Properties to return via API, id is always required
class ItemPublic(ItemBase):
    id: uuid.UUID
    owner_id: uuid.UUID


class ItemsPublic(SQLModel):
    data: list[ItemPublic]
    count: int


# Generic message
class Message(SQLModel):
    message: str


# JSON payload containing access token
class Token(SQLModel):
    access_token: str
    token_type: str = "bearer"


# Contents of JWT token
class TokenPayload(SQLModel):
    sub: Optional[str] = None


class NewPassword(SQLModel):
    token: str
    new_password: str = Field(min_length=8, max_length=40)


# New database models for the application

# User Profile model
class UserProfileBase(SQLModel):
    bio: Optional[str] = Field(default=None, max_length=1000)
    location: Optional[str] = Field(default=None, max_length=255)
    website: Optional[str] = Field(default=None, max_length=255)
    linkedin_url: Optional[str] = Field(default=None, max_length=255)
    twitter_url: Optional[str] = Field(default=None, max_length=255)
    github_url: Optional[str] = Field(default=None, max_length=255)


class UserProfileCreate(UserProfileBase):
    pass


class UserProfileUpdate(UserProfileBase):
    pass


class UserProfile(UserProfileBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="user.id", nullable=False, ondelete="CASCADE")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    user: Optional[User] = Relationship(back_populates="profile")


class UserProfilePublic(UserProfileBase):
    id: uuid.UUID
    user_id: uuid.UUID
    created_at: datetime
    updated_at: datetime


# User Resume model
class UserResumeBase(SQLModel):
    title: str = Field(max_length=255)
    content: str = Field(sa_column=Column(Text))
    is_public: bool = Field(default=False)


class UserResumeCreate(UserResumeBase):
    pass


class UserResumeUpdate(UserResumeBase):
    title: Optional[str] = Field(default=None, max_length=255)
    content: Optional[str] = Field(default=None)
    is_public: Optional[bool] = Field(default=None)


class UserResume(UserResumeBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="user.id", nullable=False, ondelete="CASCADE")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    user: Optional[User] = Relationship(back_populates="resumes")


class UserResumePublic(UserResumeBase):
    id: uuid.UUID
    user_id: uuid.UUID
    created_at: datetime
    updated_at: datetime


# Repository model
class RepoBase(SQLModel):
    name: str = Field(max_length=255)
    description: Optional[str] = Field(default=None, max_length=1000)
    url: str = Field(max_length=500)
    is_private: bool = Field(default=False)
    language: Optional[str] = Field(default=None, max_length=100)
    stars: int = Field(default=0)
    forks: int = Field(default=0)


class RepoCreate(RepoBase):
    pass


class RepoUpdate(RepoBase):
    name: Optional[str] = Field(default=None, max_length=255)
    description: Optional[str] = Field(default=None, max_length=1000)
    url: Optional[str] = Field(default=None, max_length=500)
    is_private: Optional[bool] = Field(default=None)
    language: Optional[str] = Field(default=None, max_length=100)
    stars: Optional[int] = Field(default=None)
    forks: Optional[int] = Field(default=None)


class Repo(RepoBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    owner_id: uuid.UUID = Field(foreign_key="user.id", nullable=False, ondelete="CASCADE")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    owner: Optional[User] = Relationship(back_populates="repos")


class RepoPublic(RepoBase):
    id: uuid.UUID
    owner_id: uuid.UUID
    created_at: datetime
    updated_at: datetime


# Team model
class TeamBase(SQLModel):
    name: str = Field(max_length=255)
    description: Optional[str] = Field(default=None, max_length=1000)
    is_public: bool = Field(default=True)


class TeamCreate(TeamBase):
    pass


class TeamUpdate(TeamBase):
    name: Optional[str] = Field(default=None, max_length=255)
    description: Optional[str] = Field(default=None, max_length=1000)
    is_public: Optional[bool] = Field(default=None)


class Team(TeamBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    owner_id: uuid.UUID = Field(foreign_key="user.id", nullable=False, ondelete="CASCADE")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    owner: Optional[User] = Relationship(back_populates="owned_teams")
    members: list["User"] = Relationship(back_populates="teams", link_model=TeamMember)
    ideas: list["Idea"] = Relationship(back_populates="team")
    invites: list["Invite"] = Relationship(back_populates="team")


class TeamPublic(TeamBase):
    id: uuid.UUID
    owner_id: uuid.UUID
    created_at: datetime
    updated_at: datetime


# Idea model
class IdeaBase(SQLModel):
    title: str = Field(max_length=255)
    description: str = Field(sa_column=Column(Text))
    status: str = Field(default="draft", max_length=50)  # draft, published, archived
    is_public: bool = Field(default=False)
    tags: Optional[str] = Field(default=None, max_length=500)  # JSON string of tags


class IdeaCreate(IdeaBase):
    pass


class IdeaUpdate(IdeaBase):
    title: Optional[str] = Field(default=None, max_length=255)
    description: Optional[str] = Field(default=None)
    status: Optional[str] = Field(default=None, max_length=50)
    is_public: Optional[bool] = Field(default=None)
    tags: Optional[str] = Field(default=None, max_length=500)


class Idea(IdeaBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    creator_id: uuid.UUID = Field(foreign_key="user.id", nullable=False, ondelete="CASCADE")
    team_id: Optional[uuid.UUID] = Field(foreign_key="team.id", nullable=True, ondelete="SET NULL")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    creator: Optional[User] = Relationship(back_populates="ideas")
    team: Optional[Team] = Relationship(back_populates="ideas")
    collaborators: list["IdeaCollaborator"] = Relationship(back_populates="idea")
    change_proposals: list["IdeaChangeProposal"] = Relationship(back_populates="idea")
    comments: list["Comment"] = Relationship(back_populates="idea")
    deep_dive_versions: list["DeepDiveVersion"] = Relationship(back_populates="idea")
    case_studies: list["CaseStudy"] = Relationship(back_populates="idea")
    market_snapshots: list["MarketSnapshot"] = Relationship(back_populates="idea")
    lens_insights: list["LensInsight"] = Relationship(back_populates="idea")
    vc_thesis_comparisons: list["VCThesisComparison"] = Relationship(back_populates="idea")
    investor_decks: list["InvestorDeck"] = Relationship(back_populates="idea")
    version_qnas: list["IdeaVersionQnA"] = Relationship(back_populates="idea")
    iterations: list["Iteration"] = Relationship(back_populates="idea")
    invites: list["Invite"] = Relationship(back_populates="idea")
    shortlists: list["Shortlist"] = Relationship(back_populates="ideas", link_model=ShortlistIdea)
    iterating_records: list["Iterating"] = Relationship(back_populates="idea")


class IdeaPublic(IdeaBase):
    id: uuid.UUID
    creator_id: uuid.UUID
    team_id: Optional[uuid.UUID]
    created_at: datetime
    updated_at: datetime


# Shortlist model
class ShortlistBase(SQLModel):
    name: str = Field(max_length=255)
    description: Optional[str] = Field(default=None, max_length=1000)
    is_public: bool = Field(default=False)


class ShortlistCreate(ShortlistBase):
    pass


class ShortlistUpdate(ShortlistBase):
    name: Optional[str] = Field(default=None, max_length=255)
    description: Optional[str] = Field(default=None, max_length=1000)
    is_public: Optional[bool] = Field(default=None)


class Shortlist(ShortlistBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="user.id", nullable=False, ondelete="CASCADE")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    user: Optional[User] = Relationship(back_populates="shortlists")
    ideas: list["Idea"] = Relationship(back_populates="shortlists", link_model=ShortlistIdea)


class ShortlistPublic(ShortlistBase):
    id: uuid.UUID
    user_id: uuid.UUID
    created_at: datetime
    updated_at: datetime


# DeepDiveVersion model
class DeepDiveVersionBase(SQLModel):
    title: str = Field(max_length=255)
    content: str = Field(sa_column=Column(Text))
    version: int = Field(default=1)
    status: str = Field(default="draft", max_length=50)


class DeepDiveVersionCreate(DeepDiveVersionBase):
    pass


class DeepDiveVersionUpdate(DeepDiveVersionBase):
    title: Optional[str] = Field(default=None, max_length=255)
    content: Optional[str] = Field(default=None)
    version: Optional[int] = Field(default=None)
    status: Optional[str] = Field(default=None, max_length=50)


class DeepDiveVersion(DeepDiveVersionBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    idea_id: uuid.UUID = Field(foreign_key="idea.id", nullable=False, ondelete="CASCADE")
    author_id: uuid.UUID = Field(foreign_key="user.id", nullable=False, ondelete="CASCADE")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    idea: Optional[Idea] = Relationship(back_populates="deep_dive_versions")
    author: Optional[User] = Relationship(back_populates="deep_dive_versions")


class DeepDiveVersionPublic(DeepDiveVersionBase):
    id: uuid.UUID
    idea_id: uuid.UUID
    author_id: uuid.UUID
    created_at: datetime
    updated_at: datetime


# CaseStudy model
class CaseStudyBase(SQLModel):
    title: str = Field(max_length=255)
    content: str = Field(sa_column=Column(Text))
    company_name: Optional[str] = Field(default=None, max_length=255)
    industry: Optional[str] = Field(default=None, max_length=100)
    funding_stage: Optional[str] = Field(default=None, max_length=100)


class CaseStudyCreate(CaseStudyBase):
    pass


class CaseStudyUpdate(CaseStudyBase):
    title: Optional[str] = Field(default=None, max_length=255)
    content: Optional[str] = Field(default=None)
    company_name: Optional[str] = Field(default=None, max_length=255)
    industry: Optional[str] = Field(default=None, max_length=100)
    funding_stage: Optional[str] = Field(default=None, max_length=100)


class CaseStudy(CaseStudyBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    idea_id: uuid.UUID = Field(foreign_key="idea.id", nullable=False, ondelete="CASCADE")
    author_id: uuid.UUID = Field(foreign_key="user.id", nullable=False, ondelete="CASCADE")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    idea: Optional[Idea] = Relationship(back_populates="case_studies")
    author: Optional[User] = Relationship(back_populates="case_studies")


class CaseStudyPublic(CaseStudyBase):
    id: uuid.UUID
    idea_id: uuid.UUID
    author_id: uuid.UUID
    created_at: datetime
    updated_at: datetime


# MarketSnapshot model
class MarketSnapshotBase(SQLModel):
    title: str = Field(max_length=255)
    content: str = Field(sa_column=Column(Text))
    market_size: Optional[str] = Field(default=None, max_length=255)
    growth_rate: Optional[str] = Field(default=None, max_length=100)
    key_players: Optional[str] = Field(default=None, max_length=1000)


class MarketSnapshotCreate(MarketSnapshotBase):
    pass


class MarketSnapshotUpdate(MarketSnapshotBase):
    title: Optional[str] = Field(default=None, max_length=255)
    content: Optional[str] = Field(default=None)
    market_size: Optional[str] = Field(default=None, max_length=255)
    growth_rate: Optional[str] = Field(default=None, max_length=100)
    key_players: Optional[str] = Field(default=None, max_length=1000)


class MarketSnapshot(MarketSnapshotBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    idea_id: uuid.UUID = Field(foreign_key="idea.id", nullable=False, ondelete="CASCADE")
    author_id: uuid.UUID = Field(foreign_key="user.id", nullable=False, ondelete="CASCADE")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    idea: Optional[Idea] = Relationship(back_populates="market_snapshots")
    author: Optional[User] = Relationship(back_populates="market_snapshots")


class MarketSnapshotPublic(MarketSnapshotBase):
    id: uuid.UUID
    idea_id: uuid.UUID
    author_id: uuid.UUID
    created_at: datetime
    updated_at: datetime


# LensInsight model
class LensInsightBase(SQLModel):
    title: str = Field(max_length=255)
    content: str = Field(sa_column=Column(Text))
    lens_type: str = Field(max_length=100)  # e.g., "technical", "market", "financial"
    insights: Optional[str] = Field(default=None, sa_column=Column(Text))


class LensInsightCreate(LensInsightBase):
    pass


class LensInsightUpdate(LensInsightBase):
    title: Optional[str] = Field(default=None, max_length=255)
    content: Optional[str] = Field(default=None)
    lens_type: Optional[str] = Field(default=None, max_length=100)
    insights: Optional[str] = Field(default=None)


class LensInsight(LensInsightBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    idea_id: uuid.UUID = Field(foreign_key="idea.id", nullable=False, ondelete="CASCADE")
    author_id: uuid.UUID = Field(foreign_key="user.id", nullable=False, ondelete="CASCADE")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    idea: Optional[Idea] = Relationship(back_populates="lens_insights")
    author: Optional[User] = Relationship(back_populates="lens_insights")


class LensInsightPublic(LensInsightBase):
    id: uuid.UUID
    idea_id: uuid.UUID
    author_id: uuid.UUID
    created_at: datetime
    updated_at: datetime


# VCThesisComparison model
class VCThesisComparisonBase(SQLModel):
    title: str = Field(max_length=255)
    content: str = Field(sa_column=Column(Text))
    vc_firm: Optional[str] = Field(default=None, max_length=255)
    thesis_alignment_score: Optional[float] = Field(default=None)
    notes: Optional[str] = Field(default=None, sa_column=Column(Text))


class VCThesisComparisonCreate(VCThesisComparisonBase):
    pass


class VCThesisComparisonUpdate(VCThesisComparisonBase):
    title: Optional[str] = Field(default=None, max_length=255)
    content: Optional[str] = Field(default=None)
    vc_firm: Optional[str] = Field(default=None, max_length=255)
    thesis_alignment_score: Optional[float] = Field(default=None)
    notes: Optional[str] = Field(default=None)


class VCThesisComparison(VCThesisComparisonBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    idea_id: uuid.UUID = Field(foreign_key="idea.id", nullable=False, ondelete="CASCADE")
    author_id: uuid.UUID = Field(foreign_key="user.id", nullable=False, ondelete="CASCADE")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    idea: Optional[Idea] = Relationship(back_populates="vc_thesis_comparisons")
    author: Optional[User] = Relationship(back_populates="vc_thesis_comparisons")


class VCThesisComparisonPublic(VCThesisComparisonBase):
    id: uuid.UUID
    idea_id: uuid.UUID
    author_id: uuid.UUID
    created_at: datetime
    updated_at: datetime


# InvestorDeck model
class InvestorDeckBase(SQLModel):
    title: str = Field(max_length=255)
    content: str = Field(sa_column=Column(Text))
    deck_type: str = Field(max_length=100)  # e.g., "pitch", "demo", "financial"
    version: int = Field(default=1)
    is_finalized: bool = Field(default=False)


class InvestorDeckCreate(InvestorDeckBase):
    pass


class InvestorDeckUpdate(InvestorDeckBase):
    title: Optional[str] = Field(default=None, max_length=255)
    content: Optional[str] = Field(default=None)
    deck_type: Optional[str] = Field(default=None, max_length=100)
    version: Optional[int] = Field(default=None)
    is_finalized: Optional[bool] = Field(default=None)


class InvestorDeck(InvestorDeckBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    idea_id: uuid.UUID = Field(foreign_key="idea.id", nullable=False, ondelete="CASCADE")
    author_id: uuid.UUID = Field(foreign_key="user.id", nullable=False, ondelete="CASCADE")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    idea: Optional[Idea] = Relationship(back_populates="investor_decks")
    author: Optional[User] = Relationship(back_populates="investor_decks")


class InvestorDeckPublic(InvestorDeckBase):
    id: uuid.UUID
    idea_id: uuid.UUID
    author_id: uuid.UUID
    created_at: datetime
    updated_at: datetime


# IdeaCollaborator model
class IdeaCollaboratorBase(SQLModel):
    role: str = Field(max_length=100)  # e.g., "viewer", "editor", "admin"
    permissions: Optional[str] = Field(default=None, max_length=500)  # JSON string of permissions


class IdeaCollaboratorCreate(IdeaCollaboratorBase):
    pass


class IdeaCollaboratorUpdate(IdeaCollaboratorBase):
    role: Optional[str] = Field(default=None, max_length=100)
    permissions: Optional[str] = Field(default=None, max_length=500)


class IdeaCollaborator(IdeaCollaboratorBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    idea_id: uuid.UUID = Field(foreign_key="idea.id", nullable=False, ondelete="CASCADE")
    user_id: uuid.UUID = Field(foreign_key="user.id", nullable=False, ondelete="CASCADE")
    invited_by: uuid.UUID = Field(foreign_key="user.id", nullable=False, ondelete="CASCADE")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    idea: Optional[Idea] = Relationship(back_populates="collaborators")
    user: Optional[User] = Relationship(back_populates="idea_collaborations", sa_relationship_kwargs={"foreign_keys": "[IdeaCollaborator.user_id]"})
    inviter: Optional[User] = Relationship(back_populates="sent_idea_invitations", sa_relationship_kwargs={"foreign_keys": "[IdeaCollaborator.invited_by]"})


class IdeaCollaboratorPublic(IdeaCollaboratorBase):
    id: uuid.UUID
    idea_id: uuid.UUID
    user_id: uuid.UUID
    invited_by: uuid.UUID
    created_at: datetime
    updated_at: datetime


# IdeaChangeProposal model
class IdeaChangeProposalBase(SQLModel):
    title: str = Field(max_length=255)
    description: str = Field(sa_column=Column(Text))
    proposed_changes: str = Field(sa_column=Column(Text))  # JSON string of changes
    status: str = Field(default="pending", max_length=50)  # pending, approved, rejected
    reason: Optional[str] = Field(default=None, sa_column=Column(Text))


class IdeaChangeProposalCreate(IdeaChangeProposalBase):
    pass


class IdeaChangeProposalUpdate(IdeaChangeProposalBase):
    title: Optional[str] = Field(default=None, max_length=255)
    description: Optional[str] = Field(default=None)
    proposed_changes: Optional[str] = Field(default=None)
    status: Optional[str] = Field(default=None, max_length=50)
    reason: Optional[str] = Field(default=None)


class IdeaChangeProposal(IdeaChangeProposalBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    idea_id: uuid.UUID = Field(foreign_key="idea.id", nullable=False, ondelete="CASCADE")
    proposer_id: uuid.UUID = Field(foreign_key="user.id", nullable=False, ondelete="CASCADE")
    reviewer_id: Optional[uuid.UUID] = Field(foreign_key="user.id", nullable=True, ondelete="SET NULL")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    idea: Optional[Idea] = Relationship(back_populates="change_proposals")
    proposer: Optional[User] = Relationship(back_populates="proposed_changes", sa_relationship_kwargs={"foreign_keys": "[IdeaChangeProposal.proposer_id]"})
    reviewer: Optional[User] = Relationship(back_populates="reviewed_changes", sa_relationship_kwargs={"foreign_keys": "[IdeaChangeProposal.reviewer_id]"})


class IdeaChangeProposalPublic(IdeaChangeProposalBase):
    id: uuid.UUID
    idea_id: uuid.UUID
    proposer_id: uuid.UUID
    reviewer_id: Optional[uuid.UUID]
    created_at: datetime
    updated_at: datetime


# Comment model
class CommentBase(SQLModel):
    content: str = Field(sa_column=Column(Text))
    is_edited: bool = Field(default=False)


class CommentCreate(CommentBase):
    pass


class CommentUpdate(CommentBase):
    content: Optional[str] = Field(default=None)
    is_edited: Optional[bool] = Field(default=None)


class Comment(CommentBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    idea_id: uuid.UUID = Field(foreign_key="idea.id", nullable=False, ondelete="CASCADE")
    author_id: uuid.UUID = Field(foreign_key="user.id", nullable=False, ondelete="CASCADE")
    parent_id: Optional[uuid.UUID] = Field(foreign_key="comment.id", nullable=True, ondelete="CASCADE")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    idea: Optional[Idea] = Relationship(back_populates="comments")
    author: Optional[User] = Relationship(back_populates="comments")
    parent: Optional["Comment"] = Relationship(back_populates="replies", sa_relationship_kwargs={"remote_side": "Comment.id"})
    replies: list["Comment"] = Relationship(back_populates="parent")


class CommentPublic(CommentBase):
    id: uuid.UUID
    idea_id: uuid.UUID
    author_id: uuid.UUID
    parent_id: Optional[uuid.UUID]
    created_at: datetime
    updated_at: datetime


# Invite model
class InviteBase(SQLModel):
    email: EmailStr = Field(max_length=255)
    invite_type: str = Field(max_length=50)  # "team", "idea_collaboration"
    status: str = Field(default="pending", max_length=50)  # pending, accepted, rejected, expired
    message: Optional[str] = Field(default=None, max_length=1000)


class InviteCreate(InviteBase):
    pass


class InviteUpdate(InviteBase):
    email: Optional[EmailStr] = Field(default=None, max_length=255)
    invite_type: Optional[str] = Field(default=None, max_length=50)
    status: Optional[str] = Field(default=None, max_length=50)
    message: Optional[str] = Field(default=None, max_length=1000)


class Invite(InviteBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    inviter_id: uuid.UUID = Field(foreign_key="user.id", nullable=False, ondelete="CASCADE")
    team_id: Optional[uuid.UUID] = Field(foreign_key="team.id", nullable=True, ondelete="CASCADE")
    idea_id: Optional[uuid.UUID] = Field(foreign_key="idea.id", nullable=True, ondelete="CASCADE")
    token: str = Field(max_length=255, unique=True)
    expires_at: datetime
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    inviter: Optional[User] = Relationship(back_populates="sent_invites")
    team: Optional[Team] = Relationship(back_populates="invites")
    idea: Optional[Idea] = Relationship(back_populates="invites")


class InvitePublic(InviteBase):
    id: uuid.UUID
    inviter_id: uuid.UUID
    team_id: Optional[uuid.UUID]
    idea_id: Optional[uuid.UUID]
    expires_at: datetime
    created_at: datetime
    updated_at: datetime


# IdeaVersionQnA model
class IdeaVersionQnABase(SQLModel):
    question: str = Field(sa_column=Column(Text))
    answer: Optional[str] = Field(default=None, sa_column=Column(Text))
    question_type: str = Field(max_length=100)  # e.g., "technical", "market", "financial"
    priority: int = Field(default=1)  # 1-5 priority scale


class IdeaVersionQnACreate(IdeaVersionQnABase):
    pass


class IdeaVersionQnAUpdate(IdeaVersionQnABase):
    question: Optional[str] = Field(default=None)
    answer: Optional[str] = Field(default=None)
    question_type: Optional[str] = Field(default=None, max_length=100)
    priority: Optional[int] = Field(default=None)


class IdeaVersionQnA(IdeaVersionQnABase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    idea_id: uuid.UUID = Field(foreign_key="idea.id", nullable=False, ondelete="CASCADE")
    author_id: uuid.UUID = Field(foreign_key="user.id", nullable=False, ondelete="CASCADE")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    idea: Optional[Idea] = Relationship(back_populates="version_qnas")
    author: Optional[User] = Relationship(back_populates="idea_qnas")


class IdeaVersionQnAPublic(IdeaVersionQnABase):
    id: uuid.UUID
    idea_id: uuid.UUID
    author_id: uuid.UUID
    created_at: datetime
    updated_at: datetime


# AuditLog model
class AuditLogBase(SQLModel):
    action: str = Field(max_length=255)
    entity_type: str = Field(max_length=100)
    entity_id: uuid.UUID
    old_values: Optional[str] = Field(default=None, sa_column=Column(Text))  # JSON string
    new_values: Optional[str] = Field(default=None, sa_column=Column(Text))  # JSON string
    ip_address: Optional[str] = Field(default=None, max_length=45)
    user_agent: Optional[str] = Field(default=None, max_length=500)


class AuditLogCreate(AuditLogBase):
    pass


class AuditLog(AuditLogBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: Optional[uuid.UUID] = Field(foreign_key="user.id", nullable=True, ondelete="SET NULL")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    user: Optional[User] = Relationship(back_populates="audit_logs")


class AuditLogPublic(AuditLogBase):
    id: uuid.UUID
    user_id: Optional[uuid.UUID]
    created_at: datetime


# ProfileQnA model
class ProfileQnABase(SQLModel):
    question: str = Field(sa_column=Column(Text))
    answer: Optional[str] = Field(default=None, sa_column=Column(Text))
    category: str = Field(max_length=100)  # e.g., "skills", "experience", "preferences"
    is_public: bool = Field(default=True)


class ProfileQnACreate(ProfileQnABase):
    pass


class ProfileQnAUpdate(ProfileQnABase):
    question: Optional[str] = Field(default=None)
    answer: Optional[str] = Field(default=None)
    category: Optional[str] = Field(default=None, max_length=100)
    is_public: Optional[bool] = Field(default=None)


class ProfileQnA(ProfileQnABase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="user.id", nullable=False, ondelete="CASCADE")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    user: Optional[User] = Relationship(back_populates="profile_qnas")


class ProfileQnAPublic(ProfileQnABase):
    id: uuid.UUID
    user_id: uuid.UUID
    created_at: datetime
    updated_at: datetime


# Notification model
class NotificationBase(SQLModel):
    title: str = Field(max_length=255)
    message: str = Field(sa_column=Column(Text))
    notification_type: str = Field(max_length=100)  # e.g., "idea_invite", "comment", "mention"
    is_read: bool = Field(default=False)
    extra_data: Optional[str] = Field(default=None, sa_column=Column(Text))  # JSON string for additional data


class NotificationCreate(NotificationBase):
    pass


class NotificationUpdate(NotificationBase):
    title: Optional[str] = Field(default=None, max_length=255)
    message: Optional[str] = Field(default=None)
    notification_type: Optional[str] = Field(default=None, max_length=100)
    is_read: Optional[bool] = Field(default=None)
    extra_data: Optional[str] = Field(default=None)


class Notification(NotificationBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="user.id", nullable=False, ondelete="CASCADE")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    user: Optional[User] = Relationship(back_populates="notifications")


class NotificationPublic(NotificationBase):
    id: uuid.UUID
    user_id: uuid.UUID
    created_at: datetime
    updated_at: datetime


# ExportRecord model
class ExportRecordBase(SQLModel):
    export_type: str = Field(max_length=100)  # e.g., "pdf", "docx", "json"
    entity_type: str = Field(max_length=100)  # e.g., "idea", "profile", "team"
    entity_id: uuid.UUID
    file_name: str = Field(max_length=255)
    file_size: Optional[int] = Field(default=None)
    status: str = Field(default="processing", max_length=50)  # processing, completed, failed


class ExportRecordCreate(ExportRecordBase):
    pass


class ExportRecordUpdate(ExportRecordBase):
    export_type: Optional[str] = Field(default=None, max_length=100)
    entity_type: Optional[str] = Field(default=None, max_length=100)
    entity_id: Optional[uuid.UUID] = Field(default=None)
    file_name: Optional[str] = Field(default=None, max_length=255)
    file_size: Optional[int] = Field(default=None)
    status: Optional[str] = Field(default=None, max_length=50)


class ExportRecord(ExportRecordBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="user.id", nullable=False, ondelete="CASCADE")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    user: Optional[User] = Relationship(back_populates="export_records")


class ExportRecordPublic(ExportRecordBase):
    id: uuid.UUID
    user_id: uuid.UUID
    created_at: datetime
    updated_at: datetime


# Iteration model
class IterationBase(SQLModel):
    title: str = Field(max_length=255)
    description: str = Field(sa_column=Column(Text))
    version: int = Field(default=1)
    status: str = Field(default="draft", max_length=50)  # draft, active, completed, archived
    goals: Optional[str] = Field(default=None, sa_column=Column(Text))
    outcomes: Optional[str] = Field(default=None, sa_column=Column(Text))


class IterationCreate(IterationBase):
    pass


class IterationUpdate(IterationBase):
    title: Optional[str] = Field(default=None, max_length=255)
    description: Optional[str] = Field(default=None)
    version: Optional[int] = Field(default=None)
    status: Optional[str] = Field(default=None, max_length=50)
    goals: Optional[str] = Field(default=None)
    outcomes: Optional[str] = Field(default=None)


class Iteration(IterationBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    idea_id: uuid.UUID = Field(foreign_key="idea.id", nullable=False, ondelete="CASCADE")
    author_id: uuid.UUID = Field(foreign_key="user.id", nullable=False, ondelete="CASCADE")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    idea: Optional[Idea] = Relationship(back_populates="iterations")
    author: Optional[User] = Relationship(back_populates="iterations")


class IterationPublic(IterationBase):
    id: uuid.UUID
    idea_id: uuid.UUID
    author_id: uuid.UUID
    created_at: datetime
    updated_at: datetime


# Suggested model
class SuggestedBase(SQLModel):
    entity_type: str = Field(max_length=100)  # e.g., "idea", "collaboration", "resource"
    entity_id: uuid.UUID
    suggestion_type: str = Field(max_length=100)  # e.g., "similar_idea", "potential_collaborator"
    score: float = Field(default=0.0)  # relevance/confidence score
    reason: Optional[str] = Field(default=None, sa_column=Column(Text))
    extra_data: Optional[str] = Field(default=None, sa_column=Column(Text))  # JSON string


class SuggestedCreate(SuggestedBase):
    pass


class SuggestedUpdate(SuggestedBase):
    entity_type: Optional[str] = Field(default=None, max_length=100)
    entity_id: Optional[uuid.UUID] = Field(default=None)
    suggestion_type: Optional[str] = Field(default=None, max_length=100)
    score: Optional[float] = Field(default=None)
    reason: Optional[str] = Field(default=None)
    extra_data: Optional[str] = Field(default=None)


class Suggested(SuggestedBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="user.id", nullable=False, ondelete="CASCADE")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    user: Optional[User] = Relationship(back_populates="suggestions")


class SuggestedPublic(SuggestedBase):
    id: uuid.UUID
    user_id: uuid.UUID
    created_at: datetime


# Iterating model
class IteratingBase(SQLModel):
    current_stage: str = Field(max_length=100)  # e.g., "research", "prototype", "validation"
    progress_percentage: float = Field(default=0.0)
    notes: Optional[str] = Field(default=None, sa_column=Column(Text))
    next_steps: Optional[str] = Field(default=None, sa_column=Column(Text))
    blockers: Optional[str] = Field(default=None, sa_column=Column(Text))


class IteratingCreate(IteratingBase):
    pass


class IteratingUpdate(IteratingBase):
    current_stage: Optional[str] = Field(default=None, max_length=100)
    progress_percentage: Optional[float] = Field(default=None)
    notes: Optional[str] = Field(default=None)
    next_steps: Optional[str] = Field(default=None)
    blockers: Optional[str] = Field(default=None)


class Iterating(IteratingBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    idea_id: uuid.UUID = Field(foreign_key="idea.id", nullable=False, ondelete="CASCADE")
    user_id: uuid.UUID = Field(foreign_key="user.id", nullable=False, ondelete="CASCADE")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    idea: Optional[Idea] = Relationship(back_populates="iterating_records")
    user: Optional[User] = Relationship(back_populates="iterating_records")


class IteratingPublic(IteratingBase):
    id: uuid.UUID
    idea_id: uuid.UUID
    user_id: uuid.UUID
    created_at: datetime
    updated_at: datetime


# LLMInputLog model
class LLMInputLogBase(SQLModel):
    input_text: str = Field(sa_column=Column(Text))
    input_type: str = Field(max_length=100)  # e.g., "idea_generation", "content_enhancement"
    model_name: Optional[str] = Field(default=None, max_length=100)
    parameters: Optional[str] = Field(default=None, sa_column=Column(Text))  # JSON string
    context: Optional[str] = Field(default=None, sa_column=Column(Text))  # JSON string


class LLMInputLogCreate(LLMInputLogBase):
    pass


class LLMInputLog(LLMInputLogBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: Optional[uuid.UUID] = Field(foreign_key="user.id", nullable=True, ondelete="SET NULL")
    session_id: Optional[str] = Field(default=None, max_length=255)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    user: Optional[User] = Relationship(back_populates="llm_input_logs")
    processing_logs: list["LLMProcessingLog"] = Relationship(back_populates="input_log")


class LLMInputLogPublic(LLMInputLogBase):
    id: uuid.UUID
    user_id: Optional[uuid.UUID]
    session_id: Optional[str]
    created_at: datetime


# LLMProcessingLog model
class LLMProcessingLogBase(SQLModel):
    output_text: Optional[str] = Field(default=None, sa_column=Column(Text))
    status: str = Field(default="processing", max_length=50)  # processing, completed, failed
    error_message: Optional[str] = Field(default=None, sa_column=Column(Text))
    processing_time_ms: Optional[int] = Field(default=None)
    tokens_used: Optional[int] = Field(default=None)
    cost: Optional[float] = Field(default=None)


class LLMProcessingLogCreate(LLMProcessingLogBase):
    pass


class LLMProcessingLogUpdate(LLMProcessingLogBase):
    output_text: Optional[str] = Field(default=None)
    status: Optional[str] = Field(default=None, max_length=50)
    error_message: Optional[str] = Field(default=None)
    processing_time_ms: Optional[int] = Field(default=None)
    tokens_used: Optional[int] = Field(default=None)
    cost: Optional[float] = Field(default=None)


class LLMProcessingLog(LLMProcessingLogBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    input_log_id: uuid.UUID = Field(foreign_key="llminputlog.id", nullable=False, ondelete="CASCADE")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    input_log: Optional[LLMInputLog] = Relationship(back_populates="processing_logs")


class LLMProcessingLogPublic(LLMProcessingLogBase):
    id: uuid.UUID
    input_log_id: uuid.UUID
    created_at: datetime
    updated_at: datetime
