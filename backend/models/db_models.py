"""
QuadraWealth ORM Models
SQLAlchemy models for SQLite storage.
"""
import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, Text, JSON
from backend.database import Base


class UserProfile(Base):
    """Stores user investment profile and preferences."""
    __tablename__ = "user_profiles"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(100), unique=True, nullable=False, default="default_user")
    risk_tolerance = Column(String(20), nullable=False, default="moderate")  # conservative, moderate, aggressive
    investment_goals = Column(JSON, default=list)  # ["growth", "income", "preservation"]
    preferred_sectors = Column(JSON, default=list)  # ["tech", "healthcare", "energy"]
    capital_available = Column(Float, default=10000.0)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)


class PortfolioPosition(Base):
    """Simulated stock portfolio positions."""
    __tablename__ = "portfolio_positions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, nullable=False, default=1)
    ticker = Column(String(10), nullable=False)
    shares = Column(Float, nullable=False)
    avg_cost = Column(Float, nullable=False)
    purchased_at = Column(DateTime, default=datetime.datetime.utcnow)


class SavedLead(Base):
    """Saved investment leads across all modes."""
    __tablename__ = "saved_leads"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, nullable=False, default=1)
    mode = Column(String(20), nullable=False)  # stocks, edge, yields, realestate
    lead_type = Column(String(50), nullable=False)
    title = Column(String(200), nullable=False)
    details = Column(JSON, default=dict)
    saved_at = Column(DateTime, default=datetime.datetime.utcnow)
