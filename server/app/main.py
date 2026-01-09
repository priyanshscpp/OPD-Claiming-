from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config.settings import settings
from app.routers import claims, members
from app.models.database import init_db   # ✅ ADD THIS

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="AI-powered OPD claim adjudication system"
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Auto-create PostgreSQL tables on startup
@app.on_event("startup")
def startup_event():
    init_db()   # ✅ This creates "members", "claims", etc.


# Routers
app.include_router(claims.router, prefix=settings.API_V1_PREFIX, tags=["claims"])
app.include_router(members.router, prefix=settings.API_V1_PREFIX, tags=["members"])


@app.get("/")
async def root():
    return {
        "message": "Plum OPD Claim Adjudication API",
        "version": settings.VERSION,
        "status": "running"
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy"}
