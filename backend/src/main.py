from fastapi import FastAPI

app = FastAPI()


@app.get("/health")
async def health_check():
    """
    Health check endpoint to verify if the service is running.
    """
    return {"status": "healthy"}


@app.get("/health/db")
async def db_health_check():
    """
    Health check endpoint to verify if the database is reachable.
    """
    db_status = "reachable"  # TODO: Implement actual database connection check
    return {"db_status": db_status}
