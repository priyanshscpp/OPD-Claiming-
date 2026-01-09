from sqlalchemy import Column, String, Integer, Float, DateTime, JSON, ForeignKey, Text, Boolean, ARRAY
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.models.database import Base
import uuid


def generate_uuid():
    return str(uuid.uuid4())


class Member(Base):
    __tablename__ = "members"
    
    id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    policy_id = Column(String, nullable=False)
    join_date = Column(DateTime, nullable=False)
    annual_limit_used = Column(Float, default=0.0)
    gender = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    claims = relationship("Claim", back_populates="member")


class Claim(Base):
    __tablename__ = "claims"
    
    id = Column(String, primary_key=True, index=True, default=generate_uuid)
    member_id = Column(String, ForeignKey("members.id"), nullable=False)
    submission_date = Column(DateTime(timezone=True), server_default=func.now())
    treatment_date = Column(DateTime, nullable=False)
    total_amount = Column(Float, nullable=False)
    approved_amount = Column(Float, nullable=True)
    status = Column(String, default="PENDING")
    category = Column(String, nullable=True)
    hospital_name = Column(String, nullable=True)
    is_network = Column(Boolean, default=False)
    cashless_request = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    member = relationship("Member", back_populates="claims")
    documents = relationship("Document", back_populates="claim", cascade="all, delete-orphan")
    decision = relationship("Decision", back_populates="claim", uselist=False)
    audit_logs = relationship("AuditLog", back_populates="claim", cascade="all, delete-orphan")


class Document(Base):
    __tablename__ = "documents"
    
    id = Column(String, primary_key=True, index=True, default=generate_uuid)
    claim_id = Column(String, ForeignKey("claims.id"), nullable=False)
    document_type = Column(String, nullable=False)
    file_url = Column(String, nullable=False)
    filename = Column(String, nullable=False)
    extracted_data = Column(JSON, nullable=True)
    ocr_text = Column(Text, nullable=True)
    ocr_confidence = Column(Float, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    claim = relationship("Claim", back_populates="documents")


class Decision(Base):
    __tablename__ = "decisions"
    
    id = Column(String, primary_key=True, index=True, default=generate_uuid)
    claim_id = Column(String, ForeignKey("claims.id"), nullable=False, unique=True)
    decision = Column(String, nullable=False)
    approved_amount = Column(Float, default=0.0)
    rejected_amount = Column(Float, nullable=True)
    rejection_reasons = Column(ARRAY(String), nullable=True)
    confidence_score = Column(Float, nullable=False)
    reasoning = Column(ARRAY(String), nullable=True)
    notes = Column(Text, nullable=True)
    next_steps = Column(Text, nullable=True)
    flags = Column(ARRAY(String), nullable=True)
    deductions = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    claim = relationship("Claim", back_populates="decision")


class AuditLog(Base):
    __tablename__ = "audit_logs"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    claim_id = Column(String, ForeignKey("claims.id"), nullable=False)
    action = Column(String, nullable=False)
    details = Column(JSON, nullable=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    
    claim = relationship("Claim", back_populates="audit_logs")
