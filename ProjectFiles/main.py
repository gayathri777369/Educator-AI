"""
EducatorAI - Main FastAPI application entry point
"""

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
import logging
import os
from contextlib import asynccontextmanager

from models.ai_service import AIService
from api.routes import router
from config import settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global AI service instance
ai_service = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifecycle"""
    global ai_service

    # Startup
    logger.info("Starting EducatorAI application...")
    try:
        ai_service = AIService()
        await ai_service.initialize()
        logger.info("AI service initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize AI service: {e}")
        raise

    yield

    # Shutdown
    logger.info("Shutting down EducatorAI application...")
    if ai_service:
        await ai_service.cleanup()

# Create FastAPI app
app = FastAPI(
    title="EducatorAI",
    description="Educational AI application powered by IBM Granite model",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(router, prefix="/api")

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Serve the main HTML file
@app.get("/")
async def serve_index():
    """Serve the main HTML page"""
    return FileResponse("static/index1.html")

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "EducatorAI",
        "model_loaded": ai_service is not None and ai_service.is_ready()
    }

# Make AI service available to routes
@app.middleware("http")
async def add_ai_service(request, call_next):
    """Add AI service to request state"""
    request.state.ai_service = ai_service
    response = await call_next(request)
    return response

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=5000,
        reload=True,
        log_level="info"
    )
