from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException, Query
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
import logging

from app.models.database import get_db
from app.models.db_models import Claim, Document as DBDocument, Decision as DBDecision, AuditLog, Member
from app.models.schemas import ClaimResponse, DecisionResponse, DocumentResponse
from app.services.storage_service import storage_service
from app.services.ocr_service import ocr_service
from app.services.llm_service import llm_service
from app.services.rule_engine import rule_engine
from app.services.decision_engine import decision_engine
from app.utils.helpers import generate_claim_id

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

router = APIRouter()


@router.post("/claims", response_model=dict)
async def submit_claim(
    member_id: str = Form(...),
    treatment_date: str = Form(...),
    files: List[UploadFile] = File(...),
    db: Session = Depends(get_db)
):
    try:
        logger.info(f"Received claim submission for member {member_id}")
        
        member = db.query(Member).filter(Member.id == member_id).first()
        if not member:
            raise HTTPException(status_code=404, detail=f"Member {member_id} not found")
        
        for file in files:
            validation = storage_service.validate_file(file)
            if not validation["valid"]:
                raise HTTPException(status_code=400, detail=validation["error"])
        
        claim_id = generate_claim_id()
        
        treatment_date_obj = datetime.fromisoformat(treatment_date.replace('Z', '+00:00')) if isinstance(treatment_date, str) else treatment_date
        
        claim = Claim(
            id=claim_id,
            member_id=member_id,
            treatment_date=treatment_date_obj,
            total_amount=0.0,
            status="PROCESSING"
        )
        db.add(claim)
        db.commit()
        
        audit = AuditLog(
            claim_id=claim_id,
            action="CLAIM_SUBMITTED",
            details={"member_id": member_id, "treatment_date": str(treatment_date_obj)}
        )
        db.add(audit)
        db.commit()
        
        logger.info(f"Claim {claim_id} created. Processing documents...")
        
        claim_data = {
            "id": claim_id,
            "member_id": member_id,
            "treatment_date": treatment_date,
            "documents": []
        }
        
        for file in files:
            saved_file = await storage_service.save_uploaded_file(file, claim_id)
            
            if not saved_file["success"]:
                continue
            
            file_path = saved_file["file_path"]
            
            ocr_result = await ocr_service.extract_text_from_document(file_path)
            
            if not ocr_result["success"]:
                logger.error(f"OCR failed for {file.filename}")
                continue
            
            doc_type = _detect_document_type(file.filename)
            
            extracted_data = None
            if doc_type == "prescription":
                extracted_data = await llm_service.extract_prescription_data(ocr_result["raw_text"])
            elif doc_type == "bill":
                extracted_data = await llm_service.extract_bill_data(ocr_result["raw_text"])
            elif doc_type == "report":
                extracted_data = await llm_service.extract_report_data(ocr_result["raw_text"])
            
            db_document = DBDocument(
                claim_id=claim_id,
                document_type=doc_type,
                file_url=saved_file["file_url"],
                filename=file.filename,
                extracted_data=extracted_data,
                ocr_text=ocr_result["raw_text"],
                ocr_confidence=ocr_result["confidence"]
            )
            db.add(db_document)
            db.commit()
            
            claim_data["documents"].append({
                "document_type": doc_type,
                "extracted_data": extracted_data,
                "ocr_confidence": ocr_result["confidence"]
            })
            
            logger.info(f"Document {file.filename} processed as {doc_type}")
        
        audit = AuditLog(
            claim_id=claim_id,
            action="DOCUMENTS_PROCESSED",
            details={"document_count": len(files)}
        )
        db.add(audit)
        db.commit()
        
        logger.info(f"Running validation for claim {claim_id}")
        validation_results = await rule_engine.validate_claim(claim_data, db)
        
        logger.info(f"Making decision for claim {claim_id}")
        decision_result = decision_engine.make_decision(claim_data, validation_results)
        
        bill_doc = next((d for d in claim_data["documents"] if d["document_type"] == "bill"), None)
        total_amount = 0.0
        if bill_doc and bill_doc.get("extracted_data"):
            total_amount = bill_doc["extracted_data"].get("total_amount", 0.0)
        
        claim.total_amount = total_amount
        claim.approved_amount = decision_result["approved_amount"]
        claim.status = decision_result["decision"]
        claim.category = claim_data.get("category")
        
        if bill_doc and bill_doc.get("extracted_data"):
            claim.hospital_name = bill_doc["extracted_data"].get("hospital_name")
        
        claim.is_network = claim_data.get("is_network", False)
        db.commit()
        
        db_decision = DBDecision(
            claim_id=claim_id,
            decision=decision_result["decision"],
            approved_amount=decision_result["approved_amount"],
            rejected_amount=decision_result.get("rejected_amount", 0.0),
            rejection_reasons=decision_result.get("rejection_reasons", []),
            confidence_score=decision_result["confidence_score"],
            reasoning=decision_result.get("reasoning", []),
            notes=decision_result.get("notes", ""),
            next_steps=decision_result.get("next_steps", ""),
            flags=decision_result.get("flags", []),
            deductions=decision_result.get("deductions", {})
        )
        db.add(db_decision)
        db.commit()
        
        if decision_result["decision"] == "APPROVED":
            member.annual_limit_used += decision_result["approved_amount"]
            db.commit()
        
        audit = AuditLog(
            claim_id=claim_id,
            action="DECISION_MADE",
            details={
                "decision": decision_result["decision"],
                "approved_amount": decision_result["approved_amount"],
                "confidence": decision_result["confidence_score"]
            }
        )
        db.add(audit)
        db.commit()
        
        logger.info(f"Claim {claim_id} processing complete. Decision: {decision_result['decision']}")
        
        return {
            "success": True,
            "claim_id": claim_id,
            "status": decision_result["decision"],
            "approved_amount": decision_result["approved_amount"],
            "confidence_score": decision_result["confidence_score"],
            "message": f"Claim processed. Status: {decision_result['decision']}"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing claim: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error processing claim: {str(e)}")


@router.get("/claims/{claim_id}", response_model=ClaimResponse)
async def get_claim(claim_id: str, db: Session = Depends(get_db)):
    claim = db.query(Claim).filter(Claim.id == claim_id).first()
    
    if not claim:
        raise HTTPException(status_code=404, detail=f"Claim {claim_id} not found")
    
    return claim


@router.get("/claims", response_model=List[ClaimResponse])
async def list_claims(
    member_id: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    skip: int = Query(0),
    limit: int = Query(20),
    db: Session = Depends(get_db)
):
    query = db.query(Claim)
    
    if member_id:
        query = query.filter(Claim.member_id == member_id)
    
    if status:
        query = query.filter(Claim.status == status)
    
    claims = query.order_by(Claim.created_at.desc()).offset(skip).limit(limit).all()
    
    return claims


@router.get("/decisions/{claim_id}", response_model=DecisionResponse)
async def get_decision(claim_id: str, db: Session = Depends(get_db)):
    decision = db.query(DBDecision).filter(DBDecision.claim_id == claim_id).first()
    
    if not decision:
        raise HTTPException(status_code=404, detail=f"Decision for claim {claim_id} not found")
    
    return decision


@router.get("/claims/{claim_id}/documents", response_model=List[DocumentResponse])
async def get_claim_documents(claim_id: str, db: Session = Depends(get_db)):
    claim = db.query(Claim).filter(Claim.id == claim_id).first()
    
    if not claim:
        raise HTTPException(status_code=404, detail=f"Claim {claim_id} not found")
    
    documents = db.query(DBDocument).filter(DBDocument.claim_id == claim_id).all()
    
    return documents


def _detect_document_type(filename: str) -> str:
    filename_lower = filename.lower()
    
    if any(term in filename_lower for term in ["prescription", "rx", "presc"]):
        return "prescription"
    elif any(term in filename_lower for term in ["bill", "invoice", "receipt"]):
        return "bill"
    elif any(term in filename_lower for term in ["report", "test", "lab", "diagnostic"]):
        return "report"
    
    return "bill"
