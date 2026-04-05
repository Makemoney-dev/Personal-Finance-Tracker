from sqlalchemy import Column, String, Numeric, Date, DateTime, ForeignKey, Enum
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

class Transaction(Base):
    __tablename__ = "Transactions"
    id = Column(UNIQUEIDENTIFIER, primary_key=True, default=uuid.uuid4)
    user_id = Column(UNIQUEIDENTIFIER, ForeignKey("Users.id", ondelete="CASCADE"))
    amount = Column(Numeric(18, 2), nullable=False)
    type = Column(String(10), nullable=False) # 'INCOME' or 'EXPENSE'
    category = Column(String(50), nullable=False)
    description = Column(String(255))
    transaction_date = Column(Date, nullable=False)
    owner = relationship("User", back_populates="transactions")