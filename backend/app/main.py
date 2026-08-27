import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app.config import settings
from backend.app.database import init_db
from backend.app.routers import documents, patients, search

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Initializing database...")
    await init_db()
    logger.info("Clinical Document Intelligence Hub started")
    yield
    logger.info("Shutting down")


app = FastAPI(
    title="Clinical Document Intelligence Hub",
    description="AI-powered clinical document extraction and analysis",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(documents.router)
app.include_router(search.router)
app.include_router(patients.router)


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "clinical-doc-hub"}


@app.get("/")
async def root():
    return {
        "service": "Clinical Document Intelligence Hub",
        "version": "0.1.0",
        "docs": "/docs",
    }
