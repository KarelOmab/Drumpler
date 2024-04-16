from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from .sql_base import Base  # Import the Base declarative class

class SqlJob(Base):
    __tablename__ = 'jobs'
    id = Column(Integer, primary_key=True)
    request_id = Column(Integer, nullable=False)
    created_date = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    modified_date = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    finished_date = Column(DateTime(timezone=True))
    status = Column(String)
    events = relationship("SqlEvent", backref="job")
