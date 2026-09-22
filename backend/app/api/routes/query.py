"""
API routes — GET /health and POST /query.
"""

import logging
from fastapi import APIRouter, HTTPException, status

from app.schemas.query import QueryRequest, QueryResponse
from app.services.generation import run_pipeline

logger = logging.getLogger(__name__)

router = APIRouter()


# ── Health check ──────────────────────────────────────────────────────────────
@router.get(
    "/wikipedia/status",
    summary="Wikipedia RAG status",
    tags=["Wikipedia RAG"],
    response_description="Wikipedia RAG API status",
)
async def wikipedia_status() -> dict:
    """
    Returns the live status of the Wikipedia RAG API.
    Use this endpoint for liveness / readiness probes.
    """
    return {"status": "ok", "message": "Wikipedia RAG API is running.", "project": "wikipedia-rag"}


# ── Query endpoint ────────────────────────────────────────────────────────────
@router.post(
    "/query",
    summary="Ask a Wikipedia question",
    tags=["Wikipedia RAG"],
    response_model=QueryResponse,
    responses={
        200: {"description": "Successful RAG response"},
        422: {"description": "Validation error — check request body"},
        500: {"description": "Internal server error"},
    },
)
async def query(request: QueryRequest) -> QueryResponse:
    """
    Run the full secured RAG pipeline:

    1. **Safety guardrail** — classifies the question as SAFE / UNSAFE / PROMPT_INJECTION.
    2. **Retrieval** — fetches the most relevant chunks from ChromaDB.
    3. **Generation** — builds a grounded answer with the LLM.

    Returns the answer and the source passages used.
    """
    logger.info("Received query: %r", request.question[:80])

    try:
        answer, sources, blocked = run_pipeline(request.question)
    except RuntimeError as exc:
        logger.error("Pipeline not ready: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="RAG pipeline is not ready. Please try again shortly.",
        ) from exc
    except Exception as exc:
        logger.exception("Unexpected error during pipeline execution: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred. Please try again.",
        ) from exc

    return QueryResponse(answer=answer, sources=sources, blocked=blocked)
