
from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.sql import func
from .database import Base

class Analysis(Base):
    __tablename__ = "analyses"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(255), nullable=False)
    summary = Column(Text, nullable=False)
    markers_json = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
