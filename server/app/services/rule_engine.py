from datetime import datetime
from typing import Dict, Any, List
import json
from pathlib import Path
from sqlalchemy.orm import Session
from app.models.db_models import Member, Claim
from app.models.schemas import ValidationResult
from app.utils.helpers import days_between, add_days, validate_doctor_registration, calculate_name_similarity
from app.services.llm_service import llm_service
import logging

logger = logging.getLogger(__name__)


class RuleEngine:
    def __init__(self):
        policy_path = Path(__file__).parent.parent / "config" / "policy_terms.json"
        with open(policy_path, 'r') as f:
            self.policy_terms = json.load(f)
        
        self.network_hospitals = [h.lower() for h in self.policy_terms.get("network_hospitals", [])]
        self.exclusions = [e.lower() for e in self.policy_terms.get("exclusions", [])]
    
    async def validate_claim(self, claim_data: Dict[str, Any], db: Session) -> ValidationResult:
        results = ValidationResult()
        
        await self.check_eligibility(claim_data, db, results)
        
        if results.failed:
            return results
        
        await self.validate_documents(claim_data, results)
        
        if results.failed:
            return results
        
        await self.check_coverage(claim_data, results)
        
        if results.failed:
            return results
        
        await self.validate_limits(claim_data, db, results)
        
        if results.failed:
            return results
        
        await self.check_medical_necessity(claim_data, results)
        
        await self.detect_fraud(claim_data, db, results)
        
        return results
    
    async def check_eligibility(self, claim_data: Dict[str, Any], db: Session, results: ValidationResult):
        member_id = claim_data.get("member_id")
        treatment_date_str = claim_data.get("treatment_date")
        
        member = db.query(Member).filter(Member.id == member_id).first()
        if not member:
            results.failed.append({
                "code": "MEMBER_NOT_COVERED",
                "message": f"Member ID {member_id} not found in policy records"
            })
            return
        
        claim_data["member"] = member
        claim_data["member_name"] = member.name
        
        treatment_date = datetime.fromisoformat(treatment_date_str.replace('Z', '+00:00'))
        policy_start_date = datetime.fromisoformat(self.policy_terms["effective_date"])
        
        if treatment_date < policy_start_date:
            results.failed.append({
                "code": "POLICY_INACTIVE",
                "message": "Treatment date is before policy start date"
            })
            return
        
        waiting_period_result = self._check_waiting_period(
            member.join_date,
            treatment_date,
            claim_data
        )
        
        if waiting_period_result.get("in_waiting_period"):
            results.failed.append({
                "code": "WAITING_PERIOD",
                "message": waiting_period_result["message"],
                "eligible_from": waiting_period_result.get("eligible_date")
            })
            return
        
        results.passed.append("ELIGIBILITY_CHECK")
        logger.info(f"Eligibility check passed for member {member_id}")
    
    def _check_waiting_period(self, join_date: datetime, treatment_date: datetime, claim_data: Dict[str, Any]) -> Dict[str, Any]:
        days_since_join = days_between(join_date, treatment_date)
        
        diagnosis = None
        if "documents" in claim_data:
            for doc in claim_data["documents"]:
                if doc.get("document_type") == "prescription" and doc.get("extracted_data"):
                    diagnosis = doc["extracted_data"].get("diagnosis", "")
                    break
        
        if diagnosis:
            diagnosis_lower = diagnosis.lower()
            specific_waiting = self.policy_terms["waiting_periods"].get("specific_ailments", {})
            
            for condition, days_required in specific_waiting.items():
                if condition.lower() in diagnosis_lower:
                    if days_since_join < days_required:
                        return {
                            "in_waiting_period": True,
                            "message": f"{condition.title()} has {days_required}-day waiting period. Eligible from {add_days(join_date, days_required).date()}",
                            "eligible_date": add_days(join_date, days_required).isoformat()
                        }
        
        initial_waiting = self.policy_terms["waiting_periods"]["initial_waiting"]
        if days_since_join < initial_waiting:
            return {
                "in_waiting_period": True,
                "message": f"Initial {initial_waiting}-day waiting period not completed. Eligible from {add_days(join_date, initial_waiting).date()}",
                "eligible_date": add_days(join_date, initial_waiting).isoformat()
            }
        
        return {"in_waiting_period": False}
    
    async def validate_documents(self, claim_data: Dict[str, Any], results: ValidationResult):
        documents = claim_data.get("documents", [])
        
        has_prescription = any(d.get("document_type") == "prescription" for d in documents)
        has_bill = any(d.get("document_type") == "bill" for d in documents)
        
        if not has_prescription:
            results.failed.append({
                "code": "MISSING_DOCUMENTS",
                "message": "Prescription from registered doctor is required"
            })
        
        if not has_bill:
            results.failed.append({
                "code": "MISSING_DOCUMENTS",
                "message": "Medical bill/receipt is required"
            })
        
        if results.failed:
            return
        
        prescription_doc = next((d for d in documents if d.get("document_type") == "prescription"), None)
        if prescription_doc and prescription_doc.get("extracted_data"):
            reg_number = prescription_doc["extracted_data"].get("doctor_registration")
            
            if not reg_number:
                results.failed.append({
                    "code": "DOCTOR_REG_INVALID",
                    "message": "Doctor registration number is missing"
                })
            elif not validate_doctor_registration(reg_number):
                results.warnings.append({
                    "code": "DOCTOR_REG_INVALID",
                    "message": f"Doctor registration format may be invalid: {reg_number}"
                })
        
        dates = []
        for doc in documents:
            if doc.get("extracted_data"):
                extracted = doc["extracted_data"]
                date = extracted.get("date") or extracted.get("bill_date") or extracted.get("report_date")
                if date:
                    dates.append(date)
        
        if len(set(dates)) > 1:
            results.warnings.append({
                "code": "DATE_MISMATCH",
                "message": f"Document dates differ: {', '.join(set(dates))}"
            })
        
        patient_names = []
        for doc in documents:
            if doc.get("extracted_data"):
                name = doc["extracted_data"].get("patient_name")
                if name:
                    patient_names.append(name)
        
        if patient_names and claim_data.get("member_name"):
            similarity = calculate_name_similarity(claim_data["member_name"], patient_names[0])
            
            if similarity < 0.8:
                results.warnings.append({
                    "code": "PATIENT_MISMATCH",
                    "message": f"Patient name mismatch: Policy={claim_data['member_name']}, Document={patient_names[0]} (similarity: {similarity:.2f})"
                })
        
        if not results.failed:
            results.passed.append("DOCUMENT_VALIDATION")
            logger.info("Document validation passed")
    
    async def check_coverage(self, claim_data: Dict[str, Any], results: ValidationResult):
        documents = claim_data.get("documents", [])
        
        diagnosis = ""
        treatment = ""
        
        prescription_doc = next((d for d in documents if d.get("document_type") == "prescription"), None)
        if prescription_doc and prescription_doc.get("extracted_data"):
            diagnosis = (prescription_doc["extracted_data"].get("diagnosis") or "").lower()
            treatment = (prescription_doc["extracted_data"].get("treatment") or "").lower()
        
        for exclusion in self.exclusions:
            if exclusion in diagnosis or exclusion in treatment:
                results.failed.append({
                    "code": "SERVICE_NOT_COVERED",
                    "message": f"'{exclusion.title()}' is excluded from coverage"
                })
                return
        
        category = self._categorize_claim(claim_data)
        category_config = self.policy_terms["coverage_details"].get(category)
        
        if not category_config or not category_config.get("covered"):
            results.failed.append({
                "code": "SERVICE_NOT_COVERED",
                "message": f"Category '{category}' is not covered under this policy"
            })
            return
        
        if category_config.get("pre_authorization_required"):
            bill_doc = next((d for d in documents if d.get("document_type") == "bill"), None)
            if bill_doc and bill_doc.get("extracted_data"):
                total = bill_doc["extracted_data"].get("total_amount", 0)
                if total > 10000:
                    if not claim_data.get("pre_auth_number"):
                        results.failed.append({
                            "code": "PRE_AUTH_MISSING",
                            "message": f"{category} above ₹10,000 requires pre-authorization"
                        })
                        return
        
        claim_data["category"] = category
        claim_data["category_config"] = category_config
        
        results.passed.append("COVERAGE_CHECK")
        logger.info(f"Coverage check passed. Category: {category}")
    
    def _categorize_claim(self, claim_data: Dict[str, Any]) -> str:
        documents = claim_data.get("documents", [])
        
        bill_doc = next((d for d in documents if d.get("document_type") == "bill"), None)
        if not bill_doc or not bill_doc.get("extracted_data"):
            return "consultation_fees"
        
        line_items = bill_doc["extracted_data"].get("line_items", [])
        
        for item in line_items:
            desc = item.get("description", "").lower()
            
            if any(term in desc for term in ["dental", "tooth", "root canal", "extraction", "filling"]):
                return "dental"
            
            if any(term in desc for term in ["eye", "vision", "glasses", "spectacles", "lens"]):
                return "vision"
            
            if any(term in desc for term in ["ayurveda", "ayurvedic", "homeopathy", "homeopathic", "unani"]):
                return "alternative_medicine"
        
        has_tests = any(
            any(term in item.get("description", "").lower() for term in 
                ["test", "scan", "x-ray", "ultrasound", "mri", "ct", "ecg", "blood"])
            for item in line_items
        )
        
        if has_tests:
            return "diagnostic_tests"
        
        has_medicines = any(
            any(term in item.get("description", "").lower() for term in 
                ["tablet", "capsule", "syrup", "medicine", "drug", "tab", "cap"])
            for item in line_items
        )
        
        if has_medicines:
            return "pharmacy"
        
        return "consultation_fees"
    
    async def validate_limits(self, claim_data: Dict[str, Any], db: Session, results: ValidationResult):
        documents = claim_data.get("documents", [])
        bill_doc = next((d for d in documents if d.get("document_type") == "bill"), None)
        
        if not bill_doc or not bill_doc.get("extracted_data"):
            results.failed.append({
                "code": "MISSING_DOCUMENTS",
                "message": "Medical bill is required for limit validation"
            })
            return
        
        claim_amount = bill_doc["extracted_data"].get("total_amount", 0)
        claim_data["total_amount"] = claim_amount
        
        min_claim = self.policy_terms["claim_requirements"]["minimum_claim_amount"]
        if claim_amount < min_claim:
            results.failed.append({
                "code": "BELOW_MIN_AMOUNT",
                "message": f"Claim amount ₹{claim_amount} is below minimum of ₹{min_claim}"
            })
            return
        
        per_claim_limit = self.policy_terms["coverage_details"]["per_claim_limit"]
        if claim_amount > per_claim_limit:
            results.failed.append({
                "code": "PER_CLAIM_EXCEEDED",
                "message": f"Claim amount ₹{claim_amount} exceeds per-claim limit of ₹{per_claim_limit}"
            })
            return
        
        category_config = claim_data.get("category_config", {})
        category_limit = category_config.get("sub_limit", float('inf'))
        
        if claim_amount > category_limit:
            results.warnings.append({
                "code": "SUB_LIMIT_EXCEEDED",
                "message": f"Amount exceeds {claim_data.get('category')} limit of ₹{category_limit}. Will be capped."
            })
            claim_data["capped_amount"] = category_limit
        
        member = claim_data.get("member")
        if member:
            annual_used = member.annual_limit_used or 0.0
            annual_limit = self.policy_terms["coverage_details"]["annual_limit"]
            remaining_limit = annual_limit - annual_used
            
            if remaining_limit <= 0:
                results.failed.append({
                    "code": "ANNUAL_LIMIT_EXCEEDED",
                    "message": f"Annual limit of ₹{annual_limit} has been exhausted"
                })
                return
            elif claim_amount > remaining_limit:
                results.warnings.append({
                    "code": "PARTIAL_ANNUAL_LIMIT",
                    "message": f"Only ₹{remaining_limit} remaining in annual limit. Claim will be capped."
                })
                claim_data["capped_amount"] = min(
                    claim_data.get("capped_amount", claim_amount),
                    remaining_limit
                )
        
        results.passed.append("LIMIT_VALIDATION")
        logger.info("Limit validation passed")
    
    async def check_medical_necessity(self, claim_data: Dict[str, Any], results: ValidationResult):
        documents = claim_data.get("documents", [])
        
        prescription_doc = next((d for d in documents if d.get("document_type") == "prescription"), None)
        if not prescription_doc or not prescription_doc.get("extracted_data"):
            results.warnings.append({
                "code": "MEDICAL_NECESSITY_UNKNOWN",
                "message": "Cannot validate medical necessity without prescription"
            })
            return
        
        prescription = prescription_doc["extracted_data"]
        diagnosis = prescription.get("diagnosis", "")
        medicines = prescription.get("medicines_prescribed", [])
        
        bill_doc = next((d for d in documents if d.get("document_type") == "bill"), None)
        tests = []
        if bill_doc and bill_doc.get("extracted_data"):
            line_items = bill_doc["extracted_data"].get("line_items", [])
            tests = [
                item["description"] for item in line_items 
                if any(term in item.get("description", "").lower() for term in ["test", "scan", "x-ray"])
            ]
        
        if not diagnosis:
            results.warnings.append({
                "code": "MEDICAL_NECESSITY_UNKNOWN",
                "message": "Diagnosis not found in prescription"
            })
            return
        
        evaluation = await llm_service.validate_medical_necessity(diagnosis, medicines, tests)
        
        claim_data["medical_necessity_score"] = evaluation.get("confidence", 0.5)
        
        if not evaluation.get("is_necessary"):
            results.failed.append({
                "code": "NOT_MEDICALLY_NECESSARY",
                "message": evaluation.get("reasoning", "Treatment not medically necessary"),
                "confidence": evaluation.get("confidence", 0.0)
            })
        elif evaluation.get("flags"):
            results.warnings.append({
                "code": "MEDICAL_REVIEW_NEEDED",
                "message": "; ".join(evaluation["flags"])
            })
        
        results.passed.append("MEDICAL_NECESSITY_CHECK")
        logger.info("Medical necessity check completed")
    
    async def detect_fraud(self, claim_data: Dict[str, Any], db: Session, results: ValidationResult):
        fraud_flags = []
        
        member_id = claim_data.get("member_id")
        treatment_date_str = claim_data.get("treatment_date")
        treatment_date = datetime.fromisoformat(treatment_date_str.replace('Z', '+00:00'))
        
        same_day_claims = db.query(Claim).filter(
            Claim.member_id == member_id,
            Claim.treatment_date == treatment_date,
            Claim.status.notin_(["REJECTED"])
        ).all()
        
        if len(same_day_claims) >= 3:
            fraud_flags.append("Multiple claims (3+) submitted for same date")
        
        from datetime import timedelta
        last_30_days = treatment_date - timedelta(days=30)
        recent_claims = db.query(Claim).filter(
            Claim.member_id == member_id,
            Claim.treatment_date >= last_30_days
        ).all()
        
        if len(recent_claims) > 10:
            fraud_flags.append(f"Unusual claim frequency: {len(recent_claims)} claims in 30 days")
        
        member = claim_data.get("member")
        documents = claim_data.get("documents", [])
        prescription_doc = next((d for d in documents if d.get("document_type") == "prescription"), None)
        
        if member and prescription_doc and prescription_doc.get("extracted_data"):
            diagnosis = (prescription_doc["extracted_data"].get("diagnosis") or "").lower()
            
            if member.gender == "male" and any(term in diagnosis for term in ["pregnancy", "maternity", "menstrual"]):
                fraud_flags.append("Diagnosis incompatible with member gender")
            elif member.gender == "female" and any(term in diagnosis for term in ["prostate"]):
                fraud_flags.append("Diagnosis incompatible with member gender")
        
        bill_doc = next((d for d in documents if d.get("document_type") == "bill"), None)
        if bill_doc and bill_doc.get("extracted_data"):
            bill_number = bill_doc["extracted_data"].get("bill_number")
            
            if bill_number:
                duplicate_bill = db.query(Claim).join(Claim.documents).filter(
                    Claim.id != claim_data.get("id", ""),
                    Claim.status.notin_(["REJECTED"])
                ).first()
                
                if duplicate_bill:
                    fraud_flags.append(f"Potential duplicate bill number: {bill_number}")
        
        if fraud_flags:
            results.warnings.append({
                "code": "FRAUD_INDICATORS",
                "flags": fraud_flags
            })
            
            if len(fraud_flags) >= 2:
                claim_data["requires_manual_review"] = True
        
        results.passed.append("FRAUD_CHECK")
        logger.info(f"Fraud check completed. Flags: {len(fraud_flags)}")
    
    def is_network_hospital(self, hospital_name: str) -> bool:
        if not hospital_name:
            return False
        return hospital_name.lower() in self.network_hospitals


rule_engine = RuleEngine()
