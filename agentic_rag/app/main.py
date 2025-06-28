from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger
import uuid

from .api.routes import router as api_router
from .config.settings import get_settings

# Configure Loguru to write to a file
# logger.add("debug.log", format="{time} {level} {message}", level="INFO", rotation="10 MB", catch=True)

# Initialize FastAPI app
app = FastAPI(
    title="Axiom8: Agentic RAG for n8n Workflow Generation",
    version="1.0.0",
    description="Axiom8: Agentic RAG for n8n Workflow Generation",
)

# Add CORS middleware to allow cross-origin requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    logger.info("Starting up Axiom8 server...")
    settings = get_settings()
    logger.info(f"Project: {settings.project_name}")
    logger.info(f"Debug mode: {settings.debug}")

@app.get("/health", tags=["Health"])
async def health_check():
    return {"status": "ok"}

# Include the API router
app.include_router(api_router, prefix="/api/v1")
