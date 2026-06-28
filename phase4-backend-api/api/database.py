"""
Database models and connection management for storing intermediate results.
"""

from sqlalchemy import create_engine, Column, String, Integer, Float, Text, JSON, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os

Base = declarative_base()

class Workflow(Base):
    """Workflow execution tracking."""
    __tablename__ = 'workflows'
    
    id = Column(String, primary_key=True)
    status = Column(String, default='pending')
    progress = Column(Float, default=0.0)
    current_step = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)
    error = Column(Text)
    total_reviews = Column(Integer)
    batches_processed = Column(Integer, default=0)
    total_batches = Column(Integer)

class BatchAnalysis(Base):
    """Store deterministic analysis results for each batch."""
    __tablename__ = 'batch_analyses'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    workflow_id = Column(String, index=True)
    batch_id = Column(Integer)
    patterns = Column(JSON)
    review_count = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        {'sqlite_autoincrement': True},
    )

class FinalInsights(Base):
    """Cache final synthesized insights."""
    __tablename__ = 'final_insights'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    workflow_id = Column(String, unique=True, index=True)
    insights = Column(JSON)
    generated_at = Column(DateTime, default=datetime.utcnow)
    total_reviews = Column(Integer)
    is_cached = Column(Boolean, default=True)
    
    __table_args__ = (
        {'sqlite_autoincrement': True},
    )

class DatabaseManager:
    """Manage database connections and operations."""
    
    def __init__(self, database_url: str = None):
        if database_url is None:
            # Use SQLite for development, PostgreSQL for production
            database_url = os.getenv('DATABASE_URL', 'sqlite:///./spotify_reviews.db')
        
        self.engine = create_engine(database_url)
        Base.metadata.create_all(self.engine)
        self.SessionLocal = sessionmaker(bind=self.engine)
    
    def get_session(self):
        """Get a database session."""
        return self.SessionLocal()
    
    def create_workflow(self, workflow_id: str, total_reviews: int, total_batches: int) -> Workflow:
        """Create a new workflow record."""
        session = self.get_session()
        workflow = Workflow(
            id=workflow_id,
            total_reviews=total_reviews,
            total_batches=total_batches
        )
        session.add(workflow)
        session.commit()
        session.refresh(workflow)
        session.close()
        return workflow
    
    def update_workflow(self, workflow_id: str, **kwargs) -> Workflow:
        """Update workflow status."""
        session = self.get_session()
        workflow = session.query(Workflow).filter(Workflow.id == workflow_id).first()
        if workflow:
            for key, value in kwargs.items():
                setattr(workflow, key, value)
            session.commit()
            session.refresh(workflow)
        session.close()
        return workflow
    
    def save_batch_analysis(self, workflow_id: str, batch_id: int, patterns: dict, review_count: int) -> BatchAnalysis:
        """Save batch analysis results."""
        session = self.get_session()
        batch_analysis = BatchAnalysis(
            workflow_id=workflow_id,
            batch_id=batch_id,
            patterns=patterns,
            review_count=review_count
        )
        session.add(batch_analysis)
        session.commit()
        session.refresh(batch_analysis)
        session.close()
        return batch_analysis
    
    def get_batch_analyses(self, workflow_id: str) -> list:
        """Get all batch analyses for a workflow."""
        session = self.get_session()
        analyses = session.query(BatchAnalysis).filter(
            BatchAnalysis.workflow_id == workflow_id
        ).order_by(BatchAnalysis.batch_id).all()
        session.close()
        return analyses
    
    def cache_final_insights(self, workflow_id: str, insights: dict, total_reviews: int) -> FinalInsights:
        """Cache final insights."""
        session = self.get_session()
        # Delete existing cache for this workflow
        session.query(FinalInsights).filter(FinalInsights.workflow_id == workflow_id).delete()
        
        final_insights = FinalInsights(
            workflow_id=workflow_id,
            insights=insights,
            total_reviews=total_reviews,
            is_cached=True
        )
        session.add(final_insights)
        session.commit()
        session.refresh(final_insights)
        session.close()
        return final_insights
    
    def get_cached_insights(self, workflow_id: str) -> FinalInsights:
        """Get cached insights if available."""
        session = self.get_session()
        insights = session.query(FinalInsights).filter(
            FinalInsights.workflow_id == workflow_id
        ).first()
        session.close()
        return insights
    
    def get_workflow(self, workflow_id: str) -> Workflow:
        """Get workflow by ID."""
        session = self.get_session()
        workflow = session.query(Workflow).filter(Workflow.id == workflow_id).first()
        session.close()
        return workflow
