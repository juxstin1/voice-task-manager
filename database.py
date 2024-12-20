from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime

Base = declarative_base()

class LogEntry(Base):
    __tablename__ = 'logs'
    
    id = Column(Integer, primary_key=True)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.now)
    task_id = Column(Integer, ForeignKey('tasks.id'))
    task = relationship("Task", back_populates="notes")

class Task(Base):
    __tablename__ = 'tasks'
    
    id = Column(Integer, primary_key=True)
    title = Column(String(200), nullable=False)
    description = Column(Text)
    completed = Column(Boolean, default=False)
    points = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.now)
    completed_at = Column(DateTime)
    notes = relationship("LogEntry", back_populates="task", cascade="all, delete-orphan")

def init_db():
    engine = create_engine('sqlite:///tasks.db')
    # Drop all tables if they exist
    Base.metadata.drop_all(engine)
    # Create all tables with new schema
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    return Session()

# Create database session
session = init_db()
