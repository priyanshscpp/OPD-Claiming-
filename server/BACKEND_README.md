# Backend Setup Guide

## Quick Start

### 1. Install Dependencies
```bash
cd backend
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

### 2. Configure Environment
```bash
copy .env.example .env
```

Edit `.env` and add:
```
DATABASE_URL=postgresql://user:password@localhost:5432/plum_opd
GEMINI_API_KEY=your_api_key_here
```

### 3. Setup Database
```bash
# Create PostgreSQL database
createdb plum_opd

# Initialize and seed
python setup.py
```

### 4. Run Server
```bash
python run.py
```

Server runs at: http://localhost:8000
API Docs: http://localhost:8000/docs

## API Endpoints

### Claims
- `POST /api/v1/claims` - Submit new claim with documents
- `GET /api/v1/claims/{claim_id}` - Get claim details
- `GET /api/v1/claims?member_id=EMP001` - List claims
- `GET /api/v1/decisions/{claim_id}` - Get decision details
- `GET /api/v1/claims/{claim_id}/documents` - Get claim documents

### Members
- `GET /api/v1/members` - List all members
- `GET /api/v1/members/{member_id}` - Get member details
- `POST /api/v1/members` - Create new member

## Testing

### Test API Connection
```bash
python test_api.py
```

### Submit Test Claim (using curl)
```bash
curl -X POST "http://localhost:8000/api/v1/claims" \
  -F "member_id=EMP001" \
  -F "treatment_date=2024-11-01" \
  -F "files=@prescription.jpg" \
  -F "files=@bill.pdf"
```

## Project Structure

```
backend/
├── app/
│   ├── config/
│   │   ├── settings.py          # Configuration
│   │   └── policy_terms.json    # Policy rules
│   ├── models/
│   │   ├── database.py          # DB connection
│   │   ├── db_models.py         # SQLAlchemy models
│   │   └── schemas.py           # Pydantic schemas
│   ├── routers/
│   │   ├── claims.py            # Claims API
│   │   └── members.py           # Members API
│   ├── services/
│   │   ├── ocr_service.py       # Docling OCR
│   │   ├── llm_service.py       # Gemini LLM
│   │   ├── rule_engine.py       # Validation rules
│   │   ├── decision_engine.py   # Decision logic
│   │   └── storage_service.py   # File upload
│   └── utils/
│       ├── db_init.py           # DB initialization
│       └── helpers.py           # Utility functions
├── uploads/                     # Uploaded documents
├── requirements.txt
├── setup.py                     # Database setup script
└── run.py                       # Development server
```

## Processing Flow

1. **Document Upload** → Files saved to uploads/
2. **OCR** → Docling extracts text
3. **LLM Extraction** → Gemini extracts structured data
4. **Validation** → Rule engine checks 6 validations:
   - Eligibility
   - Documents
   - Coverage
   - Limits
   - Medical Necessity
   - Fraud Detection
5. **Decision** → Decision engine makes final call
6. **Response** → APPROVED/REJECTED/PARTIAL/MANUAL_REVIEW

## Common Issues

### Database Connection Error
```
psycopg2.OperationalError: could not connect to server
```
**Solution**: Make sure PostgreSQL is running and DATABASE_URL is correct

### Gemini API Error
```
google.api_core.exceptions.Unauthenticated
```
**Solution**: Check GEMINI_API_KEY in .env file

### Module Import Error
```
ModuleNotFoundError: No module named 'docling'
```
**Solution**: Activate venv and run `pip install -r requirements.txt`

## Development

### Add New Validation Rule
Edit `app/services/rule_engine.py`:
```python
async def check_custom_rule(self, claim_data, results):
    # Your validation logic
    if condition_failed:
        results.failed.append({
            "code": "CUSTOM_ERROR",
            "message": "Explanation"
        })
```

### Modify Decision Logic
Edit `app/services/decision_engine.py`:
```python
def make_decision(self, claim_data, validation_results):
    # Your decision logic
```

## Next Steps

1. ✅ Backend complete
2. 🔄 Test with sample documents
3. 🔄 Build frontend
4. 🔄 End-to-end testing
