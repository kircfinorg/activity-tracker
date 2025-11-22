from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os
import logging

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Gamified Activity Tracker API",
    description="Backend API for the Gamified Activity & Reward Tracker",
    version="1.0.0"
)

# Configure CORS
allowed_origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

logger.info(f"CORS configured with allowed origins: {allowed_origins}")

# Initialize Firebase on startup
@app.on_event("startup")
async def startup_event():
    """Initialize services on application startup"""
    try:
        from services.firebase_service import firebase_service
        logger.info("Firebase service initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize Firebase service: {str(e)}")
        raise

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Gamified Activity Tracker API",
        "version": "1.0.0",
        "status": "running"
    }

@app.get("/health")
async def health_check():
    """
    Health check endpoint
    
    Returns:
        Dict with status and Firebase connection status
    """
    try:
        from services.firebase_service import firebase_service
        # Test Firebase connection
        firebase_service.get_db()
        firebase_healthy = True
    except Exception as e:
        logger.error(f"Firebase health check failed: {str(e)}")
        firebase_healthy = False
    
    return {
        "status": "healthy" if firebase_healthy else "degraded",
        "firebase": "connected" if firebase_healthy else "disconnected"
    }

# Include routers
from routers import auth
app.include_router(auth.router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
