"""FastAPI routes for idea management and AI workflows"""
import uuid
from typing import Any, Dict

from fastapi import APIRouter, HTTPException, Depends
from sqlmodel import func, select
from pydantic import BaseModel

from app.api.deps import CurrentUser, SessionDep
from app.models import (
    Idea, IdeaCreate, IdeaUpdate, IdeaPublic, 
    User, Message
)
from app.ai.manager import AIServiceManager

router = APIRouter(prefix="/ideas", tags=["ideas"])


# Pydantic models for AI requests
class StageTransitionRequest(BaseModel):
    """Request model for stage transitions"""
    new_stage: str
    # Stage-specific parameters
    background: str = ""
    pros_cons: str = ""
    current_iteration: str = ""
    feedback: str = ""
    goals: str = ""
    stakeholder_feedback: str = ""
    feasibility_data: str = ""
    business_case: str = ""
    implementation_plan: str = ""
    resources: str = ""
    timeline: str = ""
    outcome: str = ""
    lessons_learned: str = ""
    metrics: str = ""


class AIProcessRequest(BaseModel):
    """Request model for AI processing"""
    stage: str
    # Stage-specific parameters (same as above)
    background: str = ""
    pros_cons: str = ""
    current_iteration: str = ""
    feedback: str = ""
    goals: str = ""
    stakeholder_feedback: str = ""
    feasibility_data: str = ""
    business_case: str = ""
    implementation_plan: str = ""
    resources: str = ""
    timeline: str = ""
    outcome: str = ""
    lessons_learned: str = ""
    metrics: str = ""


@router.get("/", response_model=list[IdeaPublic])
def read_ideas(
    session: SessionDep,
    current_user: CurrentUser,
    skip: int = 0,
    limit: int = 100,
    status: str = None
) -> Any:
    """
    Retrieve ideas with optional status filtering.
    """
    statement = select(Idea)
    
    # Filter by status if provided
    if status:
        statement = statement.where(Idea.status == status)
    
    # Filter by user's access permissions
    if not current_user.is_superuser:
        statement = statement.where(
            (Idea.creator_id == current_user.id) | 
            (Idea.is_public == True)
        )
    
    statement = statement.offset(skip).limit(limit)
    ideas = session.exec(statement).all()
    
    return ideas


@router.get("/{idea_id}", response_model=IdeaPublic)
def read_idea(
    session: SessionDep,
    current_user: CurrentUser,
    idea_id: uuid.UUID
) -> Any:
    """
    Get idea by ID.
    """
    idea = session.get(Idea, idea_id)
    if not idea:
        raise HTTPException(status_code=404, detail="Idea not found")
    
    # Check permissions
    if not current_user.is_superuser and idea.creator_id != current_user.id and not idea.is_public:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    return idea


@router.post("/", response_model=IdeaPublic)
def create_idea(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    idea_in: IdeaCreate
) -> Any:
    """
    Create new idea.
    """
    idea = Idea.model_validate(idea_in, update={"creator_id": current_user.id, "team_id": None})
    session.add(idea)
    session.commit()
    session.refresh(idea)
    return idea


@router.put("/{idea_id}", response_model=IdeaPublic)
def update_idea(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    idea_id: uuid.UUID,
    idea_in: IdeaUpdate,
) -> Any:
    """
    Update an idea.
    """
    idea = session.get(Idea, idea_id)
    if not idea:
        raise HTTPException(status_code=404, detail="Idea not found")
    
    # Check permissions
    if not current_user.is_superuser and idea.creator_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    update_dict = idea_in.model_dump(exclude_unset=True)
    idea.sqlmodel_update(update_dict)
    session.add(idea)
    session.commit()
    session.refresh(idea)
    return idea


@router.delete("/{idea_id}")
def delete_idea(
    session: SessionDep,
    current_user: CurrentUser,
    idea_id: uuid.UUID
) -> Message:
    """
    Delete an idea.
    """
    idea = session.get(Idea, idea_id)
    if not idea:
        raise HTTPException(status_code=404, detail="Idea not found")
    
    # Check permissions
    if not current_user.is_superuser and idea.creator_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    session.delete(idea)
    session.commit()
    return Message(message="Idea deleted successfully")


@router.post("/{idea_id}/transition", response_model=Dict[str, Any])
def transition_idea_stage(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    idea_id: uuid.UUID,
    transition_request: StageTransitionRequest
) -> Any:
    """
    Transition an idea to a new stage and trigger AI processing.
    """
    idea = session.get(Idea, idea_id)
    if not idea:
        raise HTTPException(status_code=404, detail="Idea not found")
    
    # Check permissions
    if not current_user.is_superuser and idea.creator_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    # Store the previous stage
    previous_stage = idea.status
    
    # Update the idea status
    idea.status = transition_request.new_stage
    session.add(idea)
    session.commit()
    
    # Trigger AI processing for the new stage
    ai_manager = AIServiceManager(session)
    
    try:
        result = ai_manager.trigger_stage_transition(
            idea=idea,
            user=current_user,
            from_stage=previous_stage,
            to_stage=transition_request.new_stage,
            # Pass all possible parameters
            background=transition_request.background,
            pros_cons=transition_request.pros_cons,
            current_iteration=transition_request.current_iteration,
            feedback=transition_request.feedback,
            goals=transition_request.goals,
            stakeholder_feedback=transition_request.stakeholder_feedback,
            feasibility_data=transition_request.feasibility_data,
            business_case=transition_request.business_case,
            implementation_plan=transition_request.implementation_plan,
            resources=transition_request.resources,
            timeline=transition_request.timeline,
            outcome=transition_request.outcome,
            lessons_learned=transition_request.lessons_learned,
            metrics=transition_request.metrics
        )
        
        return {
            "message": f"Idea transitioned from {previous_stage} to {transition_request.new_stage}",
            "idea_id": idea_id,
            "ai_result": result
        }
        
    except Exception as e:
        # Rollback the status change if AI processing fails
        idea.status = previous_stage
        session.add(idea)
        session.commit()
        
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to process AI for new stage: {str(e)}"
        )


@router.post("/{idea_id}/ai-process", response_model=Dict[str, Any])
def process_idea_with_ai(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    idea_id: uuid.UUID,
    ai_request: AIProcessRequest
) -> Any:
    """
    Process an idea with AI for a specific stage without changing the idea's status.
    """
    idea = session.get(Idea, idea_id)
    if not idea:
        raise HTTPException(status_code=404, detail="Idea not found")
    
    # Check permissions
    if not current_user.is_superuser and idea.creator_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    # Process with AI
    ai_manager = AIServiceManager(session)
    
    try:
        result = ai_manager.process_idea_stage(
            idea=idea,
            user=current_user,
            stage=ai_request.stage,
            # Pass all possible parameters
            background=ai_request.background,
            pros_cons=ai_request.pros_cons,
            current_iteration=ai_request.current_iteration,
            feedback=ai_request.feedback,
            goals=ai_request.goals,
            stakeholder_feedback=ai_request.stakeholder_feedback,
            feasibility_data=ai_request.feasibility_data,
            business_case=ai_request.business_case,
            implementation_plan=ai_request.implementation_plan,
            resources=ai_request.resources,
            timeline=ai_request.timeline,
            outcome=ai_request.outcome,
            lessons_learned=ai_request.lessons_learned,
            metrics=ai_request.metrics
        )
        
        return {
            "message": f"AI processing completed for stage: {ai_request.stage}",
            "idea_id": idea_id,
            "ai_result": result
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process AI: {str(e)}"
        )


@router.get("/ai/stages", response_model=list[str])
def get_available_ai_stages(
    session: SessionDep,
    current_user: CurrentUser
) -> Any:
    """
    Get list of available AI processing stages.
    """
    ai_manager = AIServiceManager(session)
    return ai_manager.get_available_stages()