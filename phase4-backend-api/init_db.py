"""
Database initialization script for Spotify Reviews Analysis Engine.
Run this script to create the database tables.
"""

import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent))

from api.database import DatabaseManager, Base
from sqlalchemy import create_engine

def init_database():
    """Initialize the database with all required tables."""
    
    # Get database URL from environment or use default
    database_url = os.getenv('DATABASE_URL', 'sqlite:///./spotify_reviews.db')
    
    print(f"Initializing database: {database_url}")
    
    # Create engine
    engine = create_engine(database_url)
    
    # Create all tables
    Base.metadata.create_all(engine)
    
    print("✓ Database tables created successfully")
    print("  - workflows")
    print("  - batch_analyses")
    print("  - final_insights")
    
    # Test connection
    db = DatabaseManager(database_url)
    session = db.get_session()
    session.close()
    
    print("✓ Database connection verified")

if __name__ == "__main__":
    init_database()
