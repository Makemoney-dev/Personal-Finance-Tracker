from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.core.database import get_db
from app.api.dependencies import get_current_user
from app.models.domain import User, Transaction
from datetime import date, timedelta

router = APIRouter()

@router.get("/dashboard-summary")
def get_dashboard_summary(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    # Total Income & Expense
    totals = db.query(
        Transaction.type, func.sum(Transaction.amount).label('total')
    ).filter(Transaction.user_id == current_user.id).group_by(Transaction.type).all()
    
    income = next((t.total for t in totals if t.type == 'INCOME'), 0)
    expense = next((t.total for t in totals if t.type == 'EXPENSE'), 0)
    
    # Category Breakdown for Expenses
    categories = db.query(
        Transaction.category, func.sum(Transaction.amount).label('total')
    ).filter(
        Transaction.user_id == current_user.id, Transaction.type == 'EXPENSE'
    ).group_by(Transaction.category).all()
    
    # Rule-Based Insights
    insights = []
    if income > 0 and (expense / income) > 0.8:
        insights.append("Warning: Your expenses are over 80% of your income.")
    if expense == 0:
        insights.append("Great start! Start tracking your expenses.")
        
    return {
        "balance": income - expense,
        "total_income": income,
        "total_expense": expense,
        "expenses_by_category": {c.category: c.total for c in categories},
        "insights": insights
    }