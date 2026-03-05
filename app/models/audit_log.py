from sqlalchemy import Column, Integer, String, DateTime, Text, JSON
from sqlalchemy.sql import func
from app.database import Base

class AuditLog(Base):
    __tablename__ = "audit_logs"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True, nullable=True) 
    username = Column(String(50))
    ip_address = Column(String(45)) 
    action = Column(String(50), nullable=False, index=True) 
    resource = Column(String(100), nullable=False, index=True) 
    resource_id = Column(String(100))
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    endpoint = Column(String(255)) 
    method = Column(String(10)) 
    status_code = Column(Integer) 
    success = Column(String(10)) 
    request_payload = Column(JSON) 
    response_summary = Column(JSON) 
    error_message = Column(Text)
    request_id = Column(String(100), index=True) 
