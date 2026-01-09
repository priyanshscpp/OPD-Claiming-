from typing import Dict, Any
from app.models.schemas import ValidationResult
from app.services.rule_engine import rule_engine
import logging

logger = logging.getLogger(__name__)


class DecisionEngine:
    def __init__(self):
        self.rule_engine = rule_engine
    
    def make_decision(self, claim_data: Dict[str, Any], validation_results: ValidationResult) -> Dict[str, Any]:
        if validation_results.failed:
            return self._create_rejection(claim_data, validation_results)
        
        if self._needs_manual_review(claim_data, validation_results):
            return self._create_manual_review(claim_data, validation_results)
        
        approved_amount = self._calculate_approved_amount(claim_data, validation_results)
        
        original_amount = claim_data.get("total_amount", 0)
        
        if approved_amount < original_amount * 0.9:
            return self._create_partial_approval(claim_data, approved_amount, validation_results)
        
        return self._create_approval(claim_data, approved_amount, validation_results)
    
    def _calculate_approved_amount(self, claim_data: Dict[str, Any], validation_results: ValidationResult) -> float:
        amount = claim_data.get("total_amount", 0)
        
        if claim_data.get("capped_amount"):
            amount = min(amount, claim_data["capped_amount"])
        
        category_config = claim_data.get("category_config", {})
        copay_percent = category_config.get("copay_percentage", 0)
        copay_amount = amount * (copay_percent / 100)
        
        claim_data["copay_amount"] = copay_amount
        amount -= copay_amount
        
        documents = claim_data.get("documents", [])
        bill_doc = next((d for d in documents if d.get("document_type") == "bill"), None)
        
        if bill_doc and bill_doc.get("extracted_data"):
            hospital_name = bill_doc["extracted_data"].get("hospital_name", "")
            
            if self.rule_engine.is_network_hospital(hospital_name):
                discount_percent = category_config.get("network_discount", 0)
                discount_amount = amount * (discount_percent / 100)
                claim_data["network_discount"] = discount_amount
                amount -= discount_amount
                claim_data["is_network"] = True
        
        return round(amount, 2)
    
    def _calculate_confidence_score(self, claim_data: Dict[str, Any], validation_results: ValidationResult) -> float:
        score = 1.0
        
        score -= len(validation_results.warnings) * 0.05
        
        medical_necessity_score = claim_data.get("medical_necessity_score")
        if medical_necessity_score is not None:
            score = (score + medical_necessity_score) / 2
        
        documents = claim_data.get("documents", [])
        if documents:
            ocr_confidences = [
                d.get("ocr_confidence", 0.8) 
                for d in documents 
                if d.get("ocr_confidence") is not None
            ]
            if ocr_confidences:
                avg_ocr = sum(ocr_confidences) / len(ocr_confidences)
                score = (score + avg_ocr) / 2
        
        return max(0.0, min(1.0, score))
    
    def _needs_manual_review(self, claim_data: Dict[str, Any], validation_results: ValidationResult) -> bool:
        if claim_data.get("total_amount", 0) > 25000:
            return True
        
        confidence = self._calculate_confidence_score(claim_data, validation_results)
        if confidence < 0.7:
            return True
        
        if claim_data.get("requires_manual_review"):
            return True
        
        if len(validation_results.warnings) >= 3:
            return True
        
        return False
    
    def _create_approval(self, claim_data: Dict[str, Any], amount: float, validation_results: ValidationResult) -> Dict[str, Any]:
        original_amount = claim_data.get("total_amount", 0)
        
        deductions = {}
        if claim_data.get("copay_amount"):
            deductions["copay"] = claim_data["copay_amount"]
        if claim_data.get("network_discount"):
            deductions["network_discount"] = claim_data["network_discount"]
        
        reasoning = [
            "✓ All required documents validated",
            "✓ Treatment covered under policy",
            "✓ Within applicable limits",
            "✓ Medical necessity established"
        ]
        
        for check in validation_results.passed:
            reasoning.append(f"✓ {check.replace('_', ' ').title()}")
        
        notes = []
        if validation_results.warnings:
            notes = [w.get("message", "") for w in validation_results.warnings]
        
        return {
            "decision": "APPROVED",
            "approved_amount": amount,
            "rejected_amount": 0.0,
            "deductions": deductions,
            "confidence_score": self._calculate_confidence_score(claim_data, validation_results),
            "reasoning": reasoning,
            "notes": "; ".join(notes) if notes else "No issues found",
            "next_steps": "Amount will be credited to registered bank account within 3-5 business days",
            "rejection_reasons": [],
            "flags": []
        }
    
    def _create_rejection(self, claim_data: Dict[str, Any], validation_results: ValidationResult) -> Dict[str, Any]:
        rejection_reasons = [f.get("code") for f in validation_results.failed]
        reasoning = [f"✗ {f.get('message')}" for f in validation_results.failed]
        
        return {
            "decision": "REJECTED",
            "approved_amount": 0.0,
            "rejected_amount": claim_data.get("total_amount", 0),
            "rejection_reasons": rejection_reasons,
            "confidence_score": self._calculate_confidence_score(claim_data, validation_results),
            "reasoning": reasoning,
            "notes": "Please review rejection reasons. You may resubmit with corrections if applicable.",
            "next_steps": "Contact support at support@plum.com if you believe this decision is incorrect or need clarification",
            "deductions": {},
            "flags": []
        }
    
    def _create_partial_approval(self, claim_data: Dict[str, Any], amount: float, validation_results: ValidationResult) -> Dict[str, Any]:
        original_amount = claim_data.get("total_amount", 0)
        rejected_amount = original_amount - amount
        
        deductions = {}
        if claim_data.get("copay_amount"):
            deductions["copay"] = claim_data["copay_amount"]
        if claim_data.get("network_discount"):
            deductions["network_discount"] = claim_data["network_discount"]
        
        reasoning = [f"Approved ₹{amount:.2f} out of ₹{original_amount:.2f} claimed"]
        
        warning_messages = [w.get("message", "") for w in validation_results.warnings]
        reasoning.extend([f"⚠ {msg}" for msg in warning_messages])
        
        return {
            "decision": "PARTIAL",
            "approved_amount": amount,
            "rejected_amount": rejected_amount,
            "rejection_reasons": [w.get("code") for w in validation_results.warnings],
            "deductions": deductions,
            "confidence_score": self._calculate_confidence_score(claim_data, validation_results),
            "reasoning": reasoning,
            "notes": "Partial approval due to policy limits or exclusions. See reasoning for details.",
            "next_steps": "Approved amount will be credited. The rejected portion cannot be claimed.",
            "flags": []
        }
    
    def _create_manual_review(self, claim_data: Dict[str, Any], validation_results: ValidationResult) -> Dict[str, Any]:
        flags = []
        
        if claim_data.get("total_amount", 0) > 25000:
            flags.append("High value claim (>₹25,000)")
        
        confidence = self._calculate_confidence_score(claim_data, validation_results)
        if confidence < 0.7:
            flags.append(f"Low confidence score ({confidence:.2f})")
        
        if len(validation_results.warnings) >= 3:
            flags.append(f"Multiple warnings ({len(validation_results.warnings)})")
        
        for warning in validation_results.warnings:
            if warning.get("code") == "FRAUD_INDICATORS":
                flags.extend(warning.get("flags", []))
        
        reasoning = [
            "Claim requires human review due to:",
        ]
        reasoning.extend([f"• {flag}" for flag in flags])
        
        return {
            "decision": "MANUAL_REVIEW",
            "approved_amount": 0.0,
            "rejected_amount": 0.0,
            "confidence_score": confidence,
            "flags": flags,
            "reasoning": reasoning,
            "notes": "Your claim has been escalated to our review team for detailed evaluation",
            "next_steps": "You will be contacted within 48 hours. Additional information may be requested.",
            "rejection_reasons": [],
            "deductions": {}
        }


decision_engine = DecisionEngine()
