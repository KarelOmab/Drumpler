from .sql_base import Base  # Import the Base declarative class
from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean
from datetime import datetime

class SqlRequest(Base):
    __tablename__ = 'requests'
    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    source_ip = Column(String(128))
    user_agent = Column(String(256))
    method = Column(String(8))
    request_url = Column(String(256))
    request_raw = Column(Text)
    custom_value = Column(String(256))
    is_handled = Column(Integer, default=0)
    is_being_processed = Column(Boolean, default=False)
