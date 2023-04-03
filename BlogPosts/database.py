from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base

engine = create_engine("sqlite:///database.db")

SessionLocal = sessionmaker(bind=engine,autocommit=False,autoflush=False)

Base = declarative_base()

def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()
