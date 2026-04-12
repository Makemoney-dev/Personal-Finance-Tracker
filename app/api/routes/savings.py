from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.api.dependencies import get_current_user
from app.models.domain import User, SavingGoal
from pydantic import BaseModel
from typing import Optional
from datetime import date

router = APIRouter()

class GoalCreate(BaseModel):
    goal_name: str
    target_amount: float
    current_amount: Optional[float] = 0.0
    target_date: Optional[date] = None

class GoalUpdate(BaseModel):
    goal_name: Optional[str] = None
    target_amount: Optional[float] = None
    current_amount: Optional[float] = None
    target_date: Optional[date] = None

class ContributePayload(BaseModel):
    amount: float

@router.post("/", status_code=status.HTTP_201_CREATED)
def create_goal(
    payload: GoalCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    goal = SavingGoal(
        user_id=current_user.id,
        goal_name=payload.goal_name,
        target_amount=payload.target_amount,
        current_amount=payload.current_amount,
        target_date=payload.target_date,
    )
    db.add(goal)
    db.commit()
    db.refresh(goal)
    return {"message": "Saving goal created", "id": str(goal.id)}

@router.get("/")
def list_goals(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    goals = db.query(SavingGoal).filter(SavingGoal.user_id == current_user.id).all()
    return [
        {
            "id": str(g.id),
            "goal_name": g.goal_name,
            "target_amount": float(g.target_amount),
            "current_amount": float(g.current_amount),
            "target_date": g.target_date,
            "progress_pct": round((float(g.current_amount) / float(g.target_amount)) * 100, 1) if g.target_amount else 0,
            "completed": float(g.current_amount) >= float(g.target_amount),
        }
        for g in goals
    ]

@router.post("/{goal_id}/contribute")
def contribute_to_goal(
    goal_id: str,
    payload: ContributePayload,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    goal = db.query(SavingGoal).filter(
        SavingGoal.id == goal_id,
        SavingGoal.user_id == current_user.id
    ).first()
    if not goal:
        raise HTTPException(status_code=404, detail="Goal not found")
    if payload.amount <= 0:
        raise HTTPException(status_code=400, detail="Contribution amount must be positive")
    goal.current_amount = float(goal.current_amount) + payload.amount
    db.commit()
    db.refresh(goal)
    return {
        "message": "Contribution added",
        "current_amount": float(goal.current_amount),
        "progress_pct": round((float(goal.current_amount) / float(goal.target_amount)) * 100, 1),
        "completed": float(goal.current_amount) >= float(goal.target_amount),
    }

@router.put("/{goal_id}")
def update_goal(
    goal_id: str,
    payload: GoalUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    goal = db.query(SavingGoal).filter(
        SavingGoal.id == goal_id,
        SavingGoal.user_id == current_user.id
    ).first()
    if not goal:
        raise HTTPException(status_code=404, detail="Goal not found")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(goal, field, value)
    db.commit()
    db.refresh(goal)
    return {"message": "Goal updated"}

@router.delete("/{goal_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_goal(
    goal_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    goal = db.query(SavingGoal).filter(
        SavingGoal.id == goal_id,
        SavingGoal.user_id == current_user.id
    ).first()
    if not goal:
        raise HTTPException(status_code=404, detail="Goal not found")
    db.delete(goal)
    db.commit()