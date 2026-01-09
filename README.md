# OPD Claim Adjudication System

 AI-powered automated insurance claim processing system for Outpatient Department (OPD) claims




## 👤 Author

- **Priyanshu Yadav**
- Email: [priyanshs.ece@gmail.com](mailto:priyanshs.ece@gmail.com)

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Architecture](#architecture)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Running the Application](#running-the-application)
- [API Documentation](#api-documentation)
- [Project Structure](#project-structure)

## 🎯 Overview

This system automates the adjudication (approval/rejection) of OPD insurance claims using AI and rule-based validation. It processes medical documents (prescriptions, bills, lab reports), extracts data using OCR and LLM, validates against policy terms, and makes intelligent approval decisions.

### Key Capabilities

- **Document Processing**: OCR extraction using Docling
- **AI Data Extraction**: Structured data extraction using Google Gemini with few-shot prompting
- **Rule Engine**: 5 sequential validation checks (eligibility, documents, coverage, limits, medical necessity)
- **Fraud Detection**: Pattern analysis for suspicious claims
- **Decision Engine**: Automated approval/rejection with confidence scoring

## ✨ Features

### Core Features
- ✅ Multi-document upload (prescription, bill, lab reports)
- ✅ Automated OCR text extraction
- ✅ AI-powered structured data extraction
- ✅ Sequential rule-based validation
- ✅ Medical necessity verification using LLM
- ✅ Fraud pattern detection

### Decision Types
- **APPROVED**: All validations passed, amount calculated with deductions
- **REJECTED**: Hard validation failures (eligibility, coverage, limits)

## 🛠 Tech Stack


### Frontend
- **Framework**: React 18 with TypeScript
- **Build Tool**: Vite
- **Styling**: CSS3 with custom design system
- **HTTP Client**: Axios

### Backend
- **Framework**: FastAPI (Python 3.10+)
- **Database**: PostgreSQL 14+ with SQLAlchemy ORM
- **OCR**: Docling
- **LLM**: Google Gemini (gemini-1.5-flash)
- **Validation**: Pydantic
- **CORS**: FastAPI CORS Middleware


## 📦 Prerequisites

Before you begin, ensure you have the following installed:

- **Python 3.10 or higher**
- **PostgreSQL 14 or higher**
- **Node.js 18+ and npm** (for frontend)
- **Git**
- **Google Gemini API Key**

## 🚀 Installation

### 1. Clone the Repository

```bash
git clone <your-repo-url>
cd Plum2
```

### 2. Backend Setup

#### Create Virtual Environment

```bash
cd backend
python -m venv venv
```

#### Activate Virtual Environment

**Windows:**
```bash
venv\Scripts\activate
```

**macOS/Linux:**
```bash
source venv/bin/activate
```

#### Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Database Setup

#### Create PostgreSQL Database

```bash
# Login to PostgreSQL
psql -U postgres

# Create database
CREATE DATABASE plum_opd;

# Exit
\q
```

#### Initialize Database Schema

```bash
python setup.py
```

This will:
- Create all required tables
- Seed 10 test members (EMP001-EMP010)
- Load policy terms configuration

### 4. Frontend Setup

```bash
cd ../frontend
npm install
```

## ⚙️ Configuration

### Backend Configuration

Create a `.env` file in the `backend` directory:

```env
# Database
DATABASE_URL=postgresql://postgres:your_password@localhost:5432/plum_opd (your database name)

# Google Gemini API
GEMINI_API_KEY=your_gemini_api_key_here

# Application
PROJECT_NAME="Plum OPD Adjudication API"
VERSION="1.0.0"
API_V1_PREFIX="/api/v1"

# Server
HOST=0.0.0.0
PORT=8000
```

### Frontend Configuration

Create a `.env` file in the `frontend` directory:

```env
VITE_API_BASE_URL=http://localhost:8000
```

### Getting Google Gemini API Key

1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy the key to your `.env` file

## 🎮 Running the Application

### Start Backend Server

```bash
cd backend
venv\Scripts\activate  # Windows
# source venv/bin/activate  # macOS/Linux

python run.py
```

Backend will start at: `http://localhost:8000`

API Documentation: `http://localhost:8000/docs`

### Start Frontend Development Server

```bash
cd frontend
npm run dev
```

Frontend will start at: `http://localhost:5173`

### Access the Application

1. Open your browser
2. Navigate to `http://localhost:5173`
3. Submit a claim with test documents
4. View results and decision details

## 📚 API Documentation

### Interactive API Docs

FastAPI provides automatic interactive API documentation:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 📁 Project Structure

```
Plum-Ass/
├── server/
│   ├── app/
│   │   ├── config/
│   │   │   ├── settings.py           # App configuration
│   │   │   └── policy_terms.json     # Policy rules
│   │   ├── models/
│   │   │   ├── database.py           # DB connection
│   │   │   ├── db_models.py          # SQLAlchemy models
│   │   │   └── schemas.py            # Pydantic schemas
│   │   ├── routers/
│   │   │   ├── claims.py             # Claim endpoints
│   │   │   └── members.py            # Member endpoints
│   │   ├── services/
│   │   │   ├── ocr_service.py        # Docling OCR
│   │   │   ├── llm_service.py        # Gemini LLM
│   │   │   ├── rule_engine.py        # Validation logic
│   │   │   ├── decision_engine.py    # Decision logic
│   │   │   └── storage_service.py    # File handling
│   │   └── utils/
│   │       ├── db_init.py            # DB initialization
│   │       └── helpers.py            # Utility functions
│   ├── uploads/                       # Uploaded documents
│   ├── requirements.txt               # Python dependencies
│   ├── setup.py                       # Database setup
│   └── run.py                         # Development server
├── client/
│   ├── src/
│   │   ├── components/               # React components
│   │   ├── services/                 # API services
│   │   ├── App.tsx                   # Main app
│   │   └── main.tsx                  # Entry point
│   ├── package.json                  # Node dependencies
│   └── vite.config.ts                # Vite configuration
├── Instructions/                      # Assignment materials
├── Data/                             # Test data
├── OPD_CLAIM_FLOW_DIAGRAMS.md        # System architecture
├── IMPLEMENTATION_SUMMARY.md         # Implementation details
├── QUICK_START.md                    # Quick reference guide
└── README.md                         # This file
```



### Running Test Cases

```bash
cd backend
python test_api.py
```

This will test all 10 scenarios from `Instructions/test_cases.json`



### Deployment Options

- **Backend**: Railway, Render, AWS EC2, Google Cloud Run
- **Frontend**: Vercel, Netlify, AWS S3 + CloudFront
- **Database**: AWS RDS, Google Cloud SQL, Supabase

