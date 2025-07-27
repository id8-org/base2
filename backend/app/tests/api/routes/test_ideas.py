"""Tests for ideas API endpoints"""
import uuid
from fastapi.testclient import TestClient
from sqlmodel import Session

from app.core.config import settings
from app.models import Idea, IdeaCreate
from app.tests.utils.user import create_random_user


def test_create_idea(client: TestClient, superuser_token_headers: dict[str, str], db: Session) -> None:
    """Test creating a new idea"""
    data = {
        "title": "Test Idea",
        "description": "This is a test idea",
        "status": "draft"
    }
    response = client.post(
        f"{settings.API_V1_STR}/ideas/",
        headers=superuser_token_headers,
        json=data,
    )
    assert response.status_code == 200
    content = response.json()
    assert content["title"] == data["title"]
    assert content["description"] == data["description"]
    assert content["status"] == data["status"]
    assert "id" in content
    assert "creator_id" in content


def test_read_ideas(client: TestClient, superuser_token_headers: dict[str, str], db: Session) -> None:
    """Test reading ideas"""
    # Create a test idea first
    user = create_random_user(db)
    idea_data = IdeaCreate(
        title="Test Read Idea",
        description="Test description",
        status="draft"
    )
    idea = Idea.model_validate(idea_data, update={"creator_id": user.id, "team_id": None})
    db.add(idea)
    db.commit()
    
    response = client.get(
        f"{settings.API_V1_STR}/ideas/",
        headers=superuser_token_headers,
    )
    assert response.status_code == 200
    content = response.json()
    assert isinstance(content, list)


def test_read_idea_by_id(client: TestClient, superuser_token_headers: dict[str, str], db: Session) -> None:
    """Test reading a specific idea by ID"""
    user = create_random_user(db)
    idea_data = IdeaCreate(
        title="Test Specific Idea",
        description="Test description",
        status="draft"
    )
    idea = Idea.model_validate(idea_data, update={"creator_id": user.id, "team_id": None})
    db.add(idea)
    db.commit()
    db.refresh(idea)
    
    response = client.get(
        f"{settings.API_V1_STR}/ideas/{idea.id}",
        headers=superuser_token_headers,
    )
    assert response.status_code == 200
    content = response.json()
    assert content["id"] == str(idea.id)
    assert content["title"] == idea.title


def test_read_idea_not_found(client: TestClient, superuser_token_headers: dict[str, str]) -> None:
    """Test reading a non-existent idea"""
    fake_id = uuid.uuid4()
    response = client.get(
        f"{settings.API_V1_STR}/ideas/{fake_id}",
        headers=superuser_token_headers,
    )
    assert response.status_code == 404


def test_update_idea(client: TestClient, superuser_token_headers: dict[str, str], db: Session) -> None:
    """Test updating an idea"""
    user = create_random_user(db)
    idea_data = IdeaCreate(
        title="Original Title",
        description="Original description",
        status="draft"
    )
    idea = Idea.model_validate(idea_data, update={"creator_id": user.id, "team_id": None})
    db.add(idea)
    db.commit()
    db.refresh(idea)
    
    update_data = {
        "title": "Updated Title",
        "description": "Updated description"
    }
    response = client.put(
        f"{settings.API_V1_STR}/ideas/{idea.id}",
        headers=superuser_token_headers,
        json=update_data,
    )
    assert response.status_code == 200
    content = response.json()
    assert content["title"] == update_data["title"]
    assert content["description"] == update_data["description"]


def test_delete_idea(client: TestClient, superuser_token_headers: dict[str, str], db: Session) -> None:
    """Test deleting an idea"""
    user = create_random_user(db)
    idea_data = IdeaCreate(
        title="To Delete Idea",
        description="This idea will be deleted",
        status="draft"
    )
    idea = Idea.model_validate(idea_data, update={"creator_id": user.id, "team_id": None})
    db.add(idea)
    db.commit()
    db.refresh(idea)
    
    response = client.delete(
        f"{settings.API_V1_STR}/ideas/{idea.id}",
        headers=superuser_token_headers,
    )
    assert response.status_code == 200
    
    # Verify the idea is deleted
    response = client.get(
        f"{settings.API_V1_STR}/ideas/{idea.id}",
        headers=superuser_token_headers,
    )
    assert response.status_code == 404


def test_get_ai_stages(client: TestClient, superuser_token_headers: dict[str, str]) -> None:
    """Test getting available AI stages"""
    response = client.get(
        f"{settings.API_V1_STR}/ideas/ai/stages",
        headers=superuser_token_headers,
    )
    assert response.status_code == 200
    content = response.json()
    assert isinstance(content, list)
    expected_stages = ["suggested", "deep_dive", "iterating", "considering", "building", "closed"]
    assert set(content) == set(expected_stages)


def test_ai_process_idea(client: TestClient, superuser_token_headers: dict[str, str], db: Session) -> None:
    """Test AI processing of an idea"""
    user = create_random_user(db)
    idea_data = IdeaCreate(
        title="AI Process Test Idea",
        description="This idea will be processed by AI",
        status="draft"
    )
    idea = Idea.model_validate(idea_data, update={"creator_id": user.id, "team_id": None})
    db.add(idea)
    db.commit()
    db.refresh(idea)
    
    process_data = {
        "stage": "suggested",
        "background": "Some background info"
    }
    response = client.post(
        f"{settings.API_V1_STR}/ideas/{idea.id}/ai-process",
        headers=superuser_token_headers,
        json=process_data,
    )
    assert response.status_code == 200
    content = response.json()
    assert "message" in content
    assert "idea_id" in content
    assert "ai_result" in content
    assert str(idea.id) == content["idea_id"]


def test_transition_idea_stage(client: TestClient, superuser_token_headers: dict[str, str], db: Session) -> None:
    """Test transitioning an idea to a new stage"""
    user = create_random_user(db)
    idea_data = IdeaCreate(
        title="Transition Test Idea",
        description="This idea will transition stages",
        status="draft"
    )
    idea = Idea.model_validate(idea_data, update={"creator_id": user.id, "team_id": None})
    db.add(idea)
    db.commit()
    db.refresh(idea)
    
    transition_data = {
        "new_stage": "suggested",
        "background": "Some background for the transition"
    }
    response = client.post(
        f"{settings.API_V1_STR}/ideas/{idea.id}/transition",
        headers=superuser_token_headers,
        json=transition_data,
    )
    assert response.status_code == 200
    content = response.json()
    assert "message" in content
    assert "idea_id" in content
    assert "ai_result" in content
    assert str(idea.id) == content["idea_id"]
    
    # Verify the idea status was updated
    response = client.get(
        f"{settings.API_V1_STR}/ideas/{idea.id}",
        headers=superuser_token_headers,
    )
    assert response.status_code == 200
    updated_idea = response.json()
    assert updated_idea["status"] == "suggested"