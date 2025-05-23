import os
import time

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlalchemy.orm import Session

from src.core.logger import app_logger
from src.core.rate_limiter import setup_limiter
from src.database import Base, engine, get_db
from src.routers.auth import router as auth_router
from src.routers.ollama import router as ollama_router
from src.routers.user import router as user_router
from src.routers.user_settings import router as user_settings_router

# Initialize database tables
app_logger.info("Creating database tables")
Base.metadata.create_all(bind=engine)

# Create FastAPI app
app = FastAPI(
    title="rovertAIChat API",
    description="Backend API for rovertAIChat application",
    version="0.1.0",
)

# Apply rate limiter
setup_limiter(app)

# Configure CORS
origins = os.getenv(
    "FRONTEND_ORIGINS",
    "http://localhost:5173",
).split(",")

app_logger.info(f"Allowed CORS origins: {origins}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(auth_router, prefix="/api/v1")
app.include_router(user_router, prefix="/api/v1")
app.include_router(user_settings_router, prefix="/api/v1")
app.include_router(ollama_router, prefix="/api/v1")


@app.get("/health")
async def health_check():
    """
    Health check endpoint to verify if the service is running.
    """
    return {"status": "healthy"}


@app.get("/health/db")
async def health_db(db: Session = Depends(get_db)):
    """
    Health check endpoint to verify if the database is reachable.
    """
    try:
        start = time.time()
        db.execute(text("SELECT 1"))
        latency = (time.time() - start) * 1000
        return {"db_status": "reachable", "latency_ms": latency}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
