"""
FastAPI application for Voice-to-Insight pipeline.
Orchestrates real-time transcription, LLM-based analysis, and insights extraction.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging
from db.schema import init_db
from api.analysis import router as analysis_router
from api.websocket import router as websocket_router

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Voice-to-Insight API",
    description="Real-time conversation intelligence pipeline",
    version="0.1.0"
)

# Add CORS middleware for frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database on startup
@app.on_event("startup")
async def startup_event():
    logger.info("Initializing database...")
    init_db()
    logger.info("Database ready")
    logger.info("FastAPI app started")
    logger.info("Endpoints: POST /api/analyze, WS /ws/session/{session_id}")


@app.on_event("shutdown")
async def shutdown_event():
    logger.info("FastAPI app shutting down")


# Include routers
app.include_router(analysis_router)
app.include_router(websocket_router)


# Health check endpoint
@app.get("/health")
async def health_check():
    """Simple health check endpoint."""
    return {"status": "ok", "service": "voice-to-insight"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
