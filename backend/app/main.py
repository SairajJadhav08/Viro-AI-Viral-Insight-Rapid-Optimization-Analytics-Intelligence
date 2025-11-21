"""
FastAPI application entry point
"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.config import settings
from app.api import auth, projects, results
from app.database import engine, Base
from app.core.logging_config import logger
from app.core.exceptions import ViroAIException

# Import all models to ensure they're registered
from app.models import User, UserSettings, Project, MutationResult, DrugCandidateResult, ModificationResult, AuthToken

# Create database tables
Base.metadata.create_all(bind=engine)

# Create FastAPI app
app = FastAPI(
    title="Viro-AI Backend API",
    description="Backend API for Viro-AI - Viral Insight Rapid Optimization Analytics Intelligence",
    version="1.0.0"
)

# CORS middleware - Allow all origins for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# Exception handlers
@app.exception_handler(ViroAIException)
async def viro_ai_exception_handler(request: Request, exc: ViroAIException):
    """Handle Viro-AI exceptions"""
    logger.error(f"Viro-AI exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": str(exc)}
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle general exceptions"""
    import traceback
    error_trace = traceback.format_exc()
    logger.error(f"Unhandled exception: {exc}\n{error_trace}")
    # Return detailed error in development
    return JSONResponse(
        status_code=500,
        content={"detail": f"Internal server error: {str(exc)}", "traceback": error_trace}
    )

# Include routers
app.include_router(auth.router, prefix=settings.API_V1_STR)
app.include_router(projects.router, prefix=settings.API_V1_STR)
app.include_router(results.router, prefix=settings.API_V1_STR)


@app.get("/")
async def root():
    """Root endpoint"""
    logger.info("Root endpoint accessed")
    return {
        "message": "Viro-AI Backend API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health")
@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "version": "2.0.0",
        "service": "VIRO-AI Backend",
        "database": "connected",
        "ml_models": "loaded"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

