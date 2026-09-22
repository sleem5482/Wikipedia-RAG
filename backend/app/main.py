"""
FastAPI application entry point.

Responsibilities:
- Create the FastAPI app with metadata
- Register CORS middleware
- Load the vector store and LLM once via lifespan events
- Mount the API router
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes.query import router as query_router
from app.core.config import get_settings
from app.services.generation import load_llm
from app.services.retrieval import load_vector_store
from app.utils.logging_config import get_logger, setup_logging

settings = get_settings()

# Initialise logging before anything else
setup_logging(level=settings.log_level)
logger = get_logger(__name__)


# ── Lifespan ──────────────────────────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Startup / shutdown hook.

    We load both heavy resources — the ChromaDB vector store and the LLM
    chains — exactly ONCE here, rather than on every request.
    This keeps latency low and avoids repeated model loading.
    """
    logger.info("=== RAG Backend starting up ===")
    logger.info("Loading vector store from: %s", settings.vector_store_path)
    load_vector_store(settings)

    logger.info("Initialising LLM (model=%s) …", settings.groq_model)
    load_llm(settings)

    logger.info("=== Startup complete — ready to serve requests ===")
    yield
    logger.info("=== RAG Backend shutting down ===")


# ── App factory ───────────────────────────────────────────────────────────────
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description=(
        "A secured Retrieval-Augmented Generation (RAG) API backed by "
        "ChromaDB + sentence-transformers embeddings and ChatGroq as the LLM. "
        "Features built-in safety guardrails to block unsafe and prompt-injection queries."
    ),
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# ── CORS middleware ───────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routers ───────────────────────────────────────────────────────────────────
app.include_router(query_router, prefix="/api/v1")
