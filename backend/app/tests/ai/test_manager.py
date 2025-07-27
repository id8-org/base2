"""Tests for AI service manager"""
import pytest
from sqlmodel import Session

from app.ai.manager import AIServiceManager
from app.models import Idea, IdeaCreate, User, UserCreate
from app.tests.utils.user import create_random_user


def test_ai_service_manager_creation(db: Session) -> None:
    """Test AIServiceManager creation"""
    manager = AIServiceManager(db)
    assert manager.session == db
    assert len(manager._services) == 0


def test_get_available_stages(db: Session) -> None:
    """Test getting available AI stages"""
    manager = AIServiceManager(db)
    stages = manager.get_available_stages()
    
    expected_stages = ["suggested", "deep_dive", "iterating", "considering", "building", "closed"]
    assert set(stages) == set(expected_stages)


def test_get_service_valid_stage(db: Session) -> None:
    """Test getting a valid AI service"""
    manager = AIServiceManager(db)
    service = manager.get_service("suggested")
    
    assert service is not None
    assert service.get_stage_name() == "suggested"


def test_get_service_invalid_stage(db: Session) -> None:
    """Test getting an invalid AI service raises error"""
    manager = AIServiceManager(db)
    
    with pytest.raises(ValueError, match="Unknown stage: invalid_stage"):
        manager.get_service("invalid_stage")


def test_get_service_caching(db: Session) -> None:
    """Test that services are cached"""
    manager = AIServiceManager(db)
    
    service1 = manager.get_service("suggested")
    service2 = manager.get_service("suggested")
    
    # Should be the same instance (cached)
    assert service1 is service2


def test_process_idea_stage_suggested(db: Session) -> None:
    """Test processing an idea through the suggested stage"""
    # Create test user and idea
    user = create_random_user(db)
    idea_data = IdeaCreate(
        title="Test AI Idea",
        description="This is a test idea for AI processing",
        status="draft"
    )
    idea = Idea.model_validate(idea_data, update={"creator_id": user.id, "team_id": None})
    db.add(idea)
    db.commit()
    db.refresh(idea)
    
    # Process with AI
    manager = AIServiceManager(db)
    result = manager.process_idea_stage(idea, user, "suggested")
    
    # Verify result structure
    assert "success" in result
    assert "stage" in result
    assert result["stage"] == "suggested"
    
    # Check if we get either ai_output (success) or error (failure)
    if result["success"]:
        assert "ai_output" in result
    else:
        assert "error" in result
    
    # Just check that we get a proper response structure
    assert isinstance(result["success"], bool)


def test_trigger_stage_transition(db: Session) -> None:
    """Test triggering stage transition with AI processing"""
    # Create test user and idea
    user = create_random_user(db)
    idea_data = IdeaCreate(
        title="Test Transition Idea",
        description="This is a test idea for stage transition",
        status="draft"
    )
    idea = Idea.model_validate(idea_data, update={"creator_id": user.id, "team_id": None})
    db.add(idea)
    db.commit()
    db.refresh(idea)
    
    # Trigger stage transition
    manager = AIServiceManager(db)
    result = manager.trigger_stage_transition(idea, user, "draft", "suggested")
    
    # Verify result structure
    assert "success" in result
    assert "stage" in result
    assert "transition" in result
    
    # Verify transition metadata
    transition = result["transition"]
    assert transition["from_stage"] == "draft"
    assert transition["to_stage"] == "suggested"
    assert transition["triggered_by"] == user.id