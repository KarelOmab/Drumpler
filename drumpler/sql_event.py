from datetime import datetime, timezone
from sqlalchemy import Column, Integer, DateTime, ForeignKey, Text
from .sql_base import Base  # Import the Base declarative class

class SqlEvent(Base):
    __tablename__ = 'events'
    id = Column(Integer, primary_key=True)
    job_id = Column(Integer, ForeignKey('jobs.id'), nullable=False)
    timestamp = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    message = Column(Text)  # Use Text for potentially longer messages
