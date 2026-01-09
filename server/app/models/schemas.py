from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class ClaimStatus(str, Enum):
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    PARTIAL = "PARTIAL"
    MANUAL_REVIEW = "MANUAL_REVIEW"


class DocumentType(str, Enum):
    PRESCRIPTION = "prescription"
    BILL = "bill"
    REPORT = "report"


class PrescriptionExtracted(BaseModel):
    doctor_name: Optional[str] = None
    doctor_registration: Optional[str] = None
    clinic_name: Optional[str] = None
    date: Optional[str] = None
    patient_name: Optional[str] = None
    patient_age: Optional[int] = None
    diagnosis: Optional[str] = None
    medicines_prescribed: Optional[List[Dict[str, Any]]] = []
    investigations_advised: Optional[List[str]] = []


class BillExtracted(BaseModel):
    hospital_name: Optional[str] = None
    bill_number: Optional[str] = None
    bill_date: Optional[str] = None
    patient_name: Optional[str] = None
    gst_number: Optional[str] = None
    line_items: Optional[List[Dict[str, Any]]] = []
    consultation_fee: Optional[float] = 0.0
    diagnostic_tests_total: Optional[float] = 0.0
    medicines_total: Optional[float] = 0.0
    subtotal: Optional[float] = 0.0
    gst_amount: Optional[float] = 0.0
    total_amount: Optional[float] = 0.0
    payment_mode: Optional[str] = None


class ReportExtracted(BaseModel):
    lab_name: Optional[str] = None
    report_date: Optional[str] = None
    patient_name: Optional[str] = None
    tests: Optional[List[Dict[str, Any]]] = []


class DocumentCreate(BaseModel):
    document_type: DocumentType
    filename: str


class DocumentResponse(BaseModel):
    id: str
    claim_id: str
    document_type: str
    filename: str
    file_url: str
    extracted_data: Optional[Dict[str, Any]] = None
    ocr_confidence: Optional[float] = None
    created_at: datetime

    class Config:
        from_attributes = True


class ClaimCreate(BaseModel):
    member_id: str
    treatment_date: datetime
    total_amount: float = 0.0


class ClaimResponse(BaseModel):
    id: str
    member_id: str
    submission_date: datetime
    treatment_date: datetime
    total_amount: float
    approved_amount: Optional[float] = None
    status: str
    category: Optional[str] = None
    hospital_name: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class DecisionResponse(BaseModel):
    id: str
    claim_id: str
    decision: str
    approved_amount: float
    rejected_amount: Optional[float] = None
    rejection_reasons: Optional[List[str]] = []
    confidence_score: float
    reasoning: Optional[List[str]] = []
    notes: Optional[str] = None
    next_steps: Optional[str] = None
    flags: Optional[List[str]] = []
    deductions: Optional[Dict[str, float]] = {}
    created_at: datetime

    class Config:
        from_attributes = True


class ValidationResult(BaseModel):
    passed: List[str] = []
    failed: List[Dict[str, Any]] = []
    warnings: List[Dict[str, Any]] = []


class MemberCreate(BaseModel):
    id: str
    name: str
    policy_id: str
    join_date: datetime
    gender: Optional[str] = None


class MemberResponse(BaseModel):
    id: str
    name: str
    policy_id: str
    join_date: datetime
    annual_limit_used: float
    created_at: datetime

    class Config:
        from_attributes = True
