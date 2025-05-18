import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from src.core.logger import app_logger

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./test.db")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "password")
app_logger.info(
    f"Connecting to database at: {DATABASE_URL.replace(POSTGRES_PASSWORD, '*' * len(POSTGRES_PASSWORD))}"
)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
