# Database Models Overview

This document provides an overview of the comprehensive database models implemented for the idea management platform.

## Model Structure

### Core Models

#### User (existing, enhanced)
- **Purpose**: Base user model for authentication and profile management
- **New Relationships**: Connected to all other models through various relationships
- **Key Fields**: email, full_name, is_active, is_superuser

#### UserProfile
- **Purpose**: Extended user profile information
- **Relationships**: One-to-one with User
- **Key Fields**: bio, location, website, social media links

#### UserResume
- **Purpose**: User resume/CV management
- **Relationships**: Many-to-one with User
- **Key Fields**: title, content (text), is_public

### Repository Management

#### Repo
- **Purpose**: Code repository tracking
- **Relationships**: Many-to-one with User (owner)
- **Key Fields**: name, description, url, language, stars, forks

### Team Collaboration

#### Team
- **Purpose**: Team/organization management
- **Relationships**: 
  - Many-to-one with User (owner)
  - Many-to-many with User (members) via team_member link table
- **Key Fields**: name, description, is_public

#### TeamMember (Link Table)
- **Purpose**: Many-to-many relationship between Team and User
- **Fields**: team_id, user_id

### Idea Management

#### Idea
- **Purpose**: Central idea/project model
- **Relationships**: 
  - Many-to-one with User (creator)
  - Many-to-one with Team (optional)
  - One-to-many with various content models
- **Key Fields**: title, description, status, is_public, tags

#### Shortlist
- **Purpose**: User-curated idea collections
- **Relationships**: 
  - Many-to-one with User
  - Many-to-many with Idea via shortlist_idea link table
- **Key Fields**: name, description, is_public

#### ShortlistIdea (Link Table)
- **Purpose**: Many-to-many relationship between Shortlist and Idea
- **Fields**: shortlist_id, idea_id

### Content Models

#### DeepDiveVersion
- **Purpose**: Versioned deep analysis content for ideas
- **Relationships**: Many-to-one with Idea and User (author)
- **Key Fields**: title, content, version, status

#### CaseStudy
- **Purpose**: Case study analysis for ideas
- **Relationships**: Many-to-one with Idea and User (author)
- **Key Fields**: title, content, company_name, industry, funding_stage

#### MarketSnapshot
- **Purpose**: Market analysis and insights
- **Relationships**: Many-to-one with Idea and User (author)
- **Key Fields**: title, content, market_size, growth_rate, key_players

#### LensInsight
- **Purpose**: Different perspective analysis (technical, market, financial)
- **Relationships**: Many-to-one with Idea and User (author)
- **Key Fields**: title, content, lens_type, insights

#### VCThesisComparison
- **Purpose**: VC thesis alignment analysis
- **Relationships**: Many-to-one with Idea and User (author)
- **Key Fields**: title, content, vc_firm, thesis_alignment_score, notes

#### InvestorDeck
- **Purpose**: Investor presentation materials
- **Relationships**: Many-to-one with Idea and User (author)
- **Key Fields**: title, content, deck_type, version, is_finalized

### Collaboration Models

#### IdeaCollaborator
- **Purpose**: Collaboration permissions and roles for ideas
- **Relationships**: Many-to-one with Idea, User (collaborator), User (inviter)
- **Key Fields**: role, permissions

#### IdeaChangeProposal
- **Purpose**: Change proposal workflow for ideas
- **Relationships**: Many-to-one with Idea, User (proposer), User (reviewer)
- **Key Fields**: title, description, proposed_changes, status, reason

#### Comment
- **Purpose**: Hierarchical comment system
- **Relationships**: 
  - Many-to-one with Idea and User (author)
  - Self-referencing for parent/child comments
- **Key Fields**: content, is_edited, parent_id

#### Invite
- **Purpose**: Invitation system for teams and ideas
- **Relationships**: Many-to-one with User (inviter), Team (optional), Idea (optional)
- **Key Fields**: email, invite_type, status, message, token, expires_at

### Q&A Systems

#### IdeaVersionQnA
- **Purpose**: Question and answer system for idea versions
- **Relationships**: Many-to-one with Idea and User (author)
- **Key Fields**: question, answer, question_type, priority

#### ProfileQnA
- **Purpose**: User profile Q&A system
- **Relationships**: Many-to-one with User
- **Key Fields**: question, answer, category, is_public

### System Management

#### AuditLog
- **Purpose**: Activity logging for accountability
- **Relationships**: Many-to-one with User (optional)
- **Key Fields**: action, entity_type, entity_id, old_values, new_values

#### Notification
- **Purpose**: User notification system
- **Relationships**: Many-to-one with User
- **Key Fields**: title, message, notification_type, is_read, metadata

#### ExportRecord
- **Purpose**: Export tracking for various file formats
- **Relationships**: Many-to-one with User
- **Key Fields**: export_type, entity_type, entity_id, file_name, status

### Iteration Management

#### Iteration
- **Purpose**: Idea iteration tracking
- **Relationships**: Many-to-one with Idea and User (author)
- **Key Fields**: title, description, version, status, goals, outcomes

#### Iterating
- **Purpose**: Active iteration status tracking
- **Relationships**: Many-to-one with Idea and User
- **Key Fields**: current_stage, progress_percentage, notes, next_steps, blockers

### AI/ML Integration

#### Suggested
- **Purpose**: AI/system suggestion system
- **Relationships**: Many-to-one with User
- **Key Fields**: entity_type, entity_id, suggestion_type, score, reason

#### LLMInputLog
- **Purpose**: LLM interaction logging
- **Relationships**: Many-to-one with User (optional)
- **Key Fields**: input_text, input_type, model_name, parameters, context

#### LLMProcessingLog
- **Purpose**: LLM processing results and metrics
- **Relationships**: Many-to-one with LLMInputLog
- **Key Fields**: output_text, status, error_message, processing_time_ms, tokens_used, cost

## Key Design Patterns

### Consistent Structure
- All models use UUID primary keys
- Timestamp tracking (created_at, updated_at) for audit trails
- Consistent naming conventions

### Relationship Management
- Proper cascade delete policies (CASCADE, SET NULL)
- Many-to-many relationships via dedicated link table models
- Self-referencing relationships for hierarchical data

### Content Storage
- Text fields for rich content using SQLAlchemy Column types
- JSON string fields for metadata and complex data structures
- Proper field constraints and validation

### Security and Privacy
- is_public flags for content visibility
- Role-based permissions in collaboration models
- Audit logging for accountability

## Migration Information

The migration file `2024072715_add_comprehensive_models.py` creates all 27 new tables with proper:
- Foreign key constraints
- Primary key definitions
- Field types and constraints
- Index creation where appropriate

To apply the migration:
```bash
alembic upgrade head
```

To rollback:
```bash
alembic downgrade 1a31ce608336
```