from sqlalchemy import Column, String, Numeric, Date, DateTime, ForeignKey
from sqlalchemy.dialects.mssql import UNIQUEIDENTIFIER
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
from app.core.database import Base

class User(Base):
    __tablename__ = "Users"
    id = Column(UNIQUEIDENTIFIER, primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(100))
    created_at = Column(DateTime, server_default=func.now())
    transactions = relationship("Transaction", back_populates="owner")
    budgets = relationship("Budget", back_populates="owner")
    saving_goals = relationship("SavingGoal", back_populates="owner")

class Transaction(Base):
    __tablename__ = "Transactions"
    id = Column(UNIQUEIDENTIFIER, primary_key=True, default=uuid.uuid4)
    user_id = Column(UNIQUEIDENTIFIER, ForeignKey("Users.id", ondelete="CASCADE"))
    amount = Column(Numeric(18, 2), nullable=False)
    type = Column(String(10), nullable=False)
    category = Column(String(50), nullable=False)
    description = Column(String(255))
    transaction_date = Column(Date, nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    owner = relationship("User", back_populates="transactions")

class Budget(Base):
    __tablename__ = "Budgets"
    id = Column(UNIQUEIDENTIFIER, primary_key=True, default=uuid.uuid4)
    user_id = Column(UNIQUEIDENTIFIER, ForeignKey("Users.id", ondelete="CASCADE"))
    category = Column(String(50), nullable=False)
    monthly_limit = Column(Numeric(18, 2), nullable=False)
    month_year = Column(String(7), nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    owner = relationship("User", back_populates="budgets")

class SavingGoal(Base):
    __tablename__ = "SavingGoals"
    id = Column(UNIQUEIDENTIFIER, primary_key=True, default=uuid.uuid4)
    user_id = Column(UNIQUEIDENTIFIER, ForeignKey("Users.id", ondelete="CASCADE"))
    goal_name = Column(String(100), nullable=False)
    target_amount = Column(Numeric(18, 2), nullable=False)
    current_amount = Column(Numeric(18, 2), default=0.00)
    target_date = Column(Date)
    created_at = Column(DateTime, server_default=func.now())
    owner = relationship("User", back_populates="saving_goals")