from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os

load_dotenv()

# The fix: provide a fallback URL so the app doesn't crash on 'None'
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./test.db")

# Render uses PostgreSQL. If your URL starts with 'postgres://', 
# SQLAlchemy 1.4+ requires it to be 'postgresql://'
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# Logic to handle different connection arguments for SQLite vs PostgreSQL
if "sqlite" in DATABASE_URL:
    # SQLite doesn't use sslmode
    engine = create_engine(
        DATABASE_URL, 
        connect_args={"check_same_thread": False}
    )
else:
    # For PostgreSQL (Render/Supabase)
    engine = create_engine(
        DATABASE_URL,
        connect_args={"sslmode": "require"},
        pool_pre_ping=True
    )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()