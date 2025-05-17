from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlalchemy.orm import Session

from src.database import Base, engine, get_db
from src.routers import auth, user

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="rovertChat API",
    description="Backend API for RovertChat application",
    version="0.1.0",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(user.router)


@app.get("/health")
async def health_check():
    """
    Health check endpoint to verify if the service is running.
    """
    return {"status": "healthy"}


@app.get("/health/db")
async def db_health_check(db: Session = Depends(get_db)):
    """
    Health check endpoint to verify if the database is reachable.
    """
    try:
        # Execute a simple query
        db.execute(text("SELECT 1"))
        db_status = "reachable"
    except Exception as e:
        db_status = f"unreachable: {str(e)}"

    return {"db_status": db_status}
