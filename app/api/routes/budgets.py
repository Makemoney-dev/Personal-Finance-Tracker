from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.core.database import get_db
from app.api.dependencies import get_current_user
from app.models.domain import User, Budget, Transaction
from pydantic import BaseModel
from typing import Optional, List

router = APIRouter()

class BudgetCreate(BaseModel):
    category: str
    monthly_limit: float
    month_year: str  # Format: YYYY-MM

class BudgetUpdate(BaseModel):
    monthly_limit: Optional[float] = None

class BudgetOut(BaseModel):
    id: str
    category: str
    monthly_limit: float
    month_year: str

    class Config:
        from_attributes = True

@router.post("/", status_code=status.HTTP_201_CREATED)
def create_budget(
    payload: BudgetCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    existing = db.query(Budget).filter(
        Budget.user_id == current_user.id,
        Budget.category == payload.category,
        Budget.month_year == payload.month_year
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Budget for this category and month already exists")

    budget = Budget(
        user_id=current_user.id,
        category=payload.category,
        monthly_limit=payload.monthly_limit,
        month_year=payload.month_year,
    )
    db.add(budget)
    db.commit()
    db.refresh(budget)
    return {"message": "Budget created", "id": str(budget.id)}

@router.get("/")
def list_budgets(
    month_year: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(Budget).filter(Budget.user_id == current_user.id)
    if month_year:
        query = query.filter(Budget.month_year == month_year)
    budgets = query.all()

    result = []
    for b in budgets:
        year, month = b.month_year.split("-")
        spent = db.query(func.sum(Transaction.amount)).filter(
            Transaction.user_id == current_user.id,
            Transaction.type == "EXPENSE",
            Transaction.category == b.category,
            func.year(Transaction.transaction_date) == int(year),
            func.month(Transaction.transaction_date) == int(month),
        ).scalar() or 0

        result.append({
            "id": str(b.id),
            "category": b.category,
            "monthly_limit": float(b.monthly_limit),
            "month_year": b.month_year,
            "spent": float(spent),
            "remaining": float(b.monthly_limit) - float(spent),
            "over_budget": float(spent) > float(b.monthly_limit),
        })
    return result

@router.put("/{budget_id}")
def update_budget(
    budget_id: str,
    payload: BudgetUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    budget = db.query(Budget).filter(
        Budget.id == budget_id,
        Budget.user_id == current_user.id
    ).first()
    if not budget:
        raise HTTPException(status_code=404, detail="Budget not found")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(budget, field, value)
    db.commit()
    db.refresh(budget)
    return {"message": "Budget updated"}

@router.delete("/{budget_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_budget(
    budget_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    budget = db.query(Budget).filter(
        Budget.id == budget_id,
        Budget.user_id == current_user.id
    ).first()
    if not budget:
        raise HTTPException(status_code=404, detail="Budget not found")
    db.delete(budget)
    db.commit()