"""
Policy Management API endpoints
CRUD operations and evaluation for security policies.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from app.database import get_db
from app.models import Policy, PolicyExecution, User, PolicyAction
from app.schemas.policy import (
    PolicyCreate,
    PolicyUpdate,
    PolicyResponse,
    PolicyExecutionResponse,
    PolicyStatisticsResponse
)
from app.security import get_current_user
from app.services.policies import PolicyEngine

router = APIRouter(prefix="/api/policies", tags=["policies"])


@router.post("", response_model=PolicyResponse, status_code=status.HTTP_201_CREATED)
async def create_policy(
    policy_data: PolicyCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new security policy.

    Requires admin privileges.
    """
    if current_user.role.value != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can create policies"
        )

    # Validate condition structure
    if not policy_data.condition.get("triggers"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Policy must have at least one trigger"
        )

    policy = Policy(
        name=policy_data.name,
        description=policy_data.description,
        condition=policy_data.condition,
        action=policy_data.action,
        priority=policy_data.priority,
        enabled=policy_data.enabled,
        created_by=current_user.id
    )

    db.add(policy)
    db.commit()
    db.refresh(policy)

    return policy


@router.get("", response_model=List[PolicyResponse])
async def list_policies(
    enabled_only: bool = Query(False),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    List all policies with optional filtering.
    """
    query = db.query(Policy)

    if enabled_only:
        query = query.filter(Policy.enabled == True)

    policies = query.order_by(Policy.priority.asc()).offset(skip).limit(limit).all()

    return policies


# Declared before /{policy_id} so the literal path is not captured as an ID.
@router.get("/statistics", response_model=PolicyStatisticsResponse)
async def get_policy_statistics(db: Session = Depends(get_db)):
    """
    Get policy system statistics and effectiveness metrics.
    """
    return PolicyEngine.get_policy_statistics(db)


@router.get("/{policy_id}", response_model=PolicyResponse)
async def get_policy(
    policy_id: str,
    db: Session = Depends(get_db)
):
    """
    Get a specific policy by ID.
    """
    policy = db.query(Policy).filter(Policy.id == policy_id).first()

    if not policy:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Policy not found"
        )

    return policy


@router.put("/{policy_id}", response_model=PolicyResponse)
async def update_policy(
    policy_id: str,
    policy_data: PolicyUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update an existing policy.

    Requires admin privileges.
    """
    if current_user.role.value != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can update policies"
        )

    policy = db.query(Policy).filter(Policy.id == policy_id).first()

    if not policy:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Policy not found"
        )

    # Update fields
    if policy_data.name is not None:
        policy.name = policy_data.name
    if policy_data.description is not None:
        policy.description = policy_data.description
    if policy_data.condition is not None:
        if not policy_data.condition.get("triggers"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Policy must have at least one trigger"
            )
        policy.condition = policy_data.condition
    if policy_data.action is not None:
        policy.action = policy_data.action
    if policy_data.priority is not None:
        policy.priority = policy_data.priority
    if policy_data.enabled is not None:
        policy.enabled = policy_data.enabled

    policy.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(policy)

    return policy


@router.delete("/{policy_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_policy(
    policy_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Delete a policy.

    Requires admin privileges.
    """
    if current_user.role.value != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can delete policies"
        )

    policy = db.query(Policy).filter(Policy.id == policy_id).first()

    if not policy:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Policy not found"
        )

    db.delete(policy)
    db.commit()


@router.get("/{policy_id}/executions", response_model=List[PolicyExecutionResponse])
async def get_policy_executions(
    policy_id: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    Get execution history for a policy.
    """
    policy = db.query(Policy).filter(Policy.id == policy_id).first()

    if not policy:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Policy not found"
        )

    executions = db.query(PolicyExecution).filter(
        PolicyExecution.policy_id == policy_id
    ).order_by(
        PolicyExecution.executed_at.desc()
    ).offset(skip).limit(limit).all()

    return executions


@router.post("/{policy_id}/test")
async def test_policy(
    policy_id: str,
    event_data: dict,
    db: Session = Depends(get_db)
):
    """
    Test a policy against sample event data.
    Useful for validating policy rules before enabling.
    """
    policy = db.query(Policy).filter(Policy.id == policy_id).first()

    if not policy:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Policy not found"
        )

    # Evaluate policy
    result = PolicyEngine._evaluate_policy(policy, event_data)

    return {
        "policy_id": policy.id,
        "matched": result.matched,
        "action": result.action.value,
        "reasoning": result.reasoning
    }
