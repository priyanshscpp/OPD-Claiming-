# Plum OPD Claim Adjudication - Backend

FastAPI backend for automated OPD claim processing using AI.

## Tech Stack
- **Framework**: FastAPI
- **OCR**: Docling
- **LLM**: Google Gemini
- **Database**: PostgreSQL
- **Validation**: Pydantic

## Project Structure
```
backend/
├── app/
│   ├── config/         # Configuration and settings
│   ├── models/         # SQLAlchemy models and Pydantic schemas
│   ├── routers/        # API endpoints
│   ├── services/       # Business logic (OCR, LLM, Rule Engine, Decision Engine)
│   ├── utils/          # Helper functions
│   └── main.py         # FastAPI application entry point
├── uploads/            # Uploaded documents storage
├── tests/              # Unit and integration tests
├── requirements.txt    # Python dependencies
├── .env               # Environment variables (create from .env.example)
└── run.py             # Development server runner
```

## Setup

### 1. Create Virtual Environment
```bash
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Setup Environment Variables
```bash
cp .env.example .env
# Edit .env with your credentials
```

### 4. Setup Database
```bash
# Create PostgreSQL database
createdb plum_opd

# Run migrations (after creating models)
# alembic upgrade head
```

### 5. Run Development Server
```bash
python run.py
```

API will be available at: http://localhost:8000
API Documentation: http://localhost:8000/docs

## API Endpoints

### Claims
- `POST /api/v1/claims` - Submit new claim
- `GET /api/v1/claims/{claim_id}` - Get claim details
- `GET /api/v1/claims` - List claims (with filters)
- `GET /api/v1/decisions/{claim_id}` - Get decision details

## Development Workflow

1. **Models**: Define Pydantic schemas in `app/models/`
2. **Services**: Implement business logic in `app/services/`
3. **Routers**: Create API endpoints in `app/routers/`
4. **Test**: Write tests in `tests/`
