import google.generativeai as genai
from app.config.settings import settings
from typing import Dict, Any
import json
import logging
import re

logger = logging.getLogger(__name__)

genai.configure(api_key=settings.GEMINI_API_KEY)


class LLMService:
    def __init__(self):
        self.model = genai.GenerativeModel('gemini-2.5-flash')
    
    def _parse_json_response(self, response_text: str) -> Dict[str, Any]:
        cleaned_text = response_text.strip()
        
        if cleaned_text.startswith('```'):
            cleaned_text = re.sub(r'^```(?:json)?\s*\n', '', cleaned_text)
            cleaned_text = re.sub(r'\n```\s*$', '', cleaned_text)
        
        return json.loads(cleaned_text.strip())
    
    async def extract_prescription_data(self, ocr_text: str) -> Dict[str, Any]:
        prompt = self._build_prescription_extraction_prompt(ocr_text)
        
        try:
            response = self.model.generate_content(prompt)
            extracted_data = self._parse_json_response(response.text)
            return extracted_data
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON from LLM response: {e}")
            logger.error(f"Response text: {response.text}")
            return self._get_empty_prescription_structure()
        except Exception as e:
            logger.error(f"Prescription extraction failed: {e}")
            return self._get_empty_prescription_structure()
    
    async def extract_bill_data(self, ocr_text: str) -> Dict[str, Any]:
        prompt = self._build_bill_extraction_prompt(ocr_text)
        
        try:
            response = self.model.generate_content(prompt)
            extracted_data = self._parse_json_response(response.text)
            return extracted_data
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON from LLM response: {e}")
            return self._get_empty_bill_structure()
        except Exception as e:
            logger.error(f"Bill extraction failed: {e}")
            return self._get_empty_bill_structure()
    
    async def extract_report_data(self, ocr_text: str) -> Dict[str, Any]:
        prompt = self._build_report_extraction_prompt(ocr_text)
        
        try:
            response = self.model.generate_content(prompt)
            extracted_data = self._parse_json_response(response.text)
            return extracted_data
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON from LLM response: {e}")
            return self._get_empty_report_structure()
        except Exception as e:
            logger.error(f"Report extraction failed: {e}")
            return self._get_empty_report_structure()
    
    async def validate_medical_necessity(self, diagnosis: str, medicines: list, tests: list) -> Dict[str, Any]:
        prompt = f"""
You are a medical claims reviewer. Evaluate if the treatment is medically necessary.

**Diagnosis**: {diagnosis}
**Medicines Prescribed**: {', '.join([m.get('name', '') for m in medicines]) if medicines else 'None'}
**Tests Ordered**: {', '.join(tests) if tests else 'None'}

Evaluate:
1. Do the medicines align with the diagnosis?
2. Are the tests relevant to the diagnosis?
3. Is the treatment following standard medical protocols?

Return ONLY a valid JSON object with this exact structure:
{{
  "is_necessary": true or false,
  "confidence": 0.0 to 1.0,
  "reasoning": "detailed explanation",
  "flags": ["list of any concerns"]
}}
"""
        
        try:
            response = self.model.generate_content(prompt)
            result = self._parse_json_response(response.text)
            return result
        except Exception as e:
            logger.error(f"Medical necessity validation failed: {e}")
            return {
                "is_necessary": True,
                "confidence": 0.5,
                "reasoning": "Unable to validate medical necessity automatically",
                "flags": ["Automatic validation failed"]
            }
    
    def _build_prescription_extraction_prompt(self, ocr_text: str) -> str:
        return f"""
Extract information from this medical prescription with HIGH ACCURACY.

**FEW-SHOT EXAMPLES:**

**Example 1 Input:**
Dr. Ramesh Sharma, MBBS, MD
Reg. No: KA/45678/2015
City Clinic, Bangalore
Date: 01/11/2024
Patient: Rajesh Kumar, Age: 35/M
Diagnosis: Viral fever
Rx:
1. Tab. Paracetamol 650mg - TDS x 3 days
2. Tab. Vitamin C 500mg - OD x 5 days

**Example 1 Output:**
{{
  "doctor_name": "Dr. Ramesh Sharma",
  "doctor_registration": "KA/45678/2015",
  "clinic_name": "City Clinic",
  "date": "2024-11-01",
  "patient_name": "Rajesh Kumar",
  "patient_age": 35,
  "diagnosis": "Viral fever",
  "medicines_prescribed": [
    {{"name": "Paracetamol 650mg", "dosage": "TDS", "duration": "3 days"}},
    {{"name": "Vitamin C 500mg", "dosage": "OD", "duration": "5 days"}}
  ],
  "investigations_advised": []
}}

**Example 2 Input:**
Dr. Priya Patel
MH/23456/2018
Apollo Dental Clinic
Date: 15-10-2024
Patient: Priya Singh, 28 years, Female
Diagnosis: Tooth decay requiring root canal
Treatment: Root canal therapy advised

**Example 2 Output:**
{{
  "doctor_name": "Dr. Priya Patel",
  "doctor_registration": "MH/23456/2018",
  "clinic_name": "Apollo Dental Clinic",
  "date": "2024-10-15",
  "patient_name": "Priya Singh",
  "patient_age": 28,
  "diagnosis": "Tooth decay requiring root canal",
  "medicines_prescribed": [],
  "investigations_advised": ["Root canal therapy"]
}}

**NOW EXTRACT FROM THIS DOCUMENT:**

{ocr_text}

**IMPORTANT INSTRUCTIONS:**
- Numbers must be EXACT (no approximation)
- Dates must be in YYYY-MM-DD format
- If a field is unclear or missing, set it to null
- Doctor registration format: STATE/NUMBER/YEAR
- Return ONLY valid JSON, no additional text

Return JSON:
"""
    
    def _build_bill_extraction_prompt(self, ocr_text: str) -> str:
        return f"""
Extract information from this medical bill with HIGH ACCURACY.

**FEW-SHOT EXAMPLES:**

**Example 1 Input:**
City Hospital
Bill No: BL001, Date: 01/11/2024
Patient: Rajesh Kumar
GST No: 29ABCDE1234F1Z5

Consultation Fee: ₹1,000
CBC Test: ₹400
Dengue Test: ₹100

Subtotal: ₹1,500
GST (18%): ₹270
Total: ₹1,770

**Example 1 Output:**
{{
  "hospital_name": "City Hospital",
  "bill_number": "BL001",
  "bill_date": "2024-11-01",
  "patient_name": "Rajesh Kumar",
  "gst_number": "29ABCDE1234F1Z5",
  "line_items": [
    {{"description": "Consultation Fee", "amount": 1000, "category": "consultation"}},
    {{"description": "CBC Test", "amount": 400, "category": "diagnostic_tests"}},
    {{"description": "Dengue Test", "amount": 100, "category": "diagnostic_tests"}}
  ],
  "consultation_fee": 1000,
  "diagnostic_tests_total": 500,
  "medicines_total": 0,
  "subtotal": 1500,
  "gst_amount": 270,
  "total_amount": 1770,
  "payment_mode": null
}}

**NOW EXTRACT FROM THIS DOCUMENT:**

{ocr_text}

**IMPORTANT INSTRUCTIONS:**
- All amounts must be numbers (remove ₹ symbol)
- Categories: "consultation", "diagnostic_tests", "medicines", "procedures", "other"
- Calculate totals accurately
- If unclear, mark as null
- Return ONLY valid JSON, no additional text

Return JSON:
"""
    
    def _build_report_extraction_prompt(self, ocr_text: str) -> str:
        return f"""
Extract information from this diagnostic test report with HIGH ACCURACY.

**FEW-SHOT EXAMPLE:**

**Example Input:**
PathLab Diagnostics
NABL Accredited
Patient: Rajesh Kumar, Age: 35/M
Date: 01/11/2024
Report ID: RPT12345

Complete Blood Count (CBC):
Hemoglobin: 14.5 g/dL (Normal: 13-17)
WBC Count: 7800 /cumm (Normal: 4000-11000)
Platelets: 250000 /cumm (Normal: 150000-450000)

**Example Output:**
{{
  "lab_name": "PathLab Diagnostics",
  "report_date": "2024-11-01",
  "patient_name": "Rajesh Kumar",
  "tests": [
    {{"test_name": "Hemoglobin", "result": "14.5", "normal_range": "13-17", "unit": "g/dL"}},
    {{"test_name": "WBC Count", "result": "7800", "normal_range": "4000-11000", "unit": "/cumm"}},
    {{"test_name": "Platelets", "result": "250000", "normal_range": "150000-450000", "unit": "/cumm"}}
  ]
}}

**NOW EXTRACT FROM THIS DOCUMENT:**

{ocr_text}

**IMPORTANT:**
- Extract ALL test results
- Preserve numbers exactly
- Return ONLY valid JSON

Return JSON:
"""
    
    def _get_empty_prescription_structure(self) -> Dict[str, Any]:
        return {
            "doctor_name": None,
            "doctor_registration": None,
            "clinic_name": None,
            "date": None,
            "patient_name": None,
            "patient_age": None,
            "diagnosis": None,
            "medicines_prescribed": [],
            "investigations_advised": []
        }
    
    def _get_empty_bill_structure(self) -> Dict[str, Any]:
        return {
            "hospital_name": None,
            "bill_number": None,
            "bill_date": None,
            "patient_name": None,
            "gst_number": None,
            "line_items": [],
            "consultation_fee": 0.0,
            "diagnostic_tests_total": 0.0,
            "medicines_total": 0.0,
            "subtotal": 0.0,
            "gst_amount": 0.0,
            "total_amount": 0.0,
            "payment_mode": None
        }
    
    def _get_empty_report_structure(self) -> Dict[str, Any]:
        return {
            "lab_name": None,
            "report_date": None,
            "patient_name": None,
            "tests": []
        }


llm_service = LLMService()
