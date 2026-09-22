"""
Retrieval service — loads ChromaDB vector store once and exposes a retriever.

The public API is:
    load_vector_store(settings)  -> called at app startup
    retrieve(question, k)        -> returns list[Document]
"""

import logging
import os
from pathlib import Path

# Disable xet download protocol (can hang on Windows) and symlinks warning
os.environ.setdefault("HF_HUB_DISABLE_XET_BACKEND", "1")
os.environ.setdefault("HF_HUB_DISABLE_SYMLINKS_WARNING", "1")

import chromadb
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

from app.core.config import Settings

logger = logging.getLogger(__name__)

# Module-level singletons — populated once at startup
_vectorstore: Chroma | None = None
_retriever = None


def load_vector_store(settings: Settings) -> None:
    """
    Initialise the ChromaDB client, embedding model, and LangChain Chroma
    wrapper.  Call this ONCE during the FastAPI lifespan startup hook.
    """
    global _vectorstore, _retriever

    store_path: Path = settings.vector_store_path_resolved
    logger.info("Loading ChromaDB from: %s", store_path)

    if not store_path.exists():
        raise FileNotFoundError(
            f"Vector store directory not found: {store_path}\n"
            "Copy your exported ChromaDB into backend/data/vector_store/ first."
        )

    # Persistent ChromaDB client
    chroma_client = chromadb.PersistentClient(path=str(store_path))

    # Sentence-Transformers embeddings (same model used in the notebook)
    embeddings = HuggingFaceEmbeddings(model_name=settings.embedding_model)

    # LangChain Chroma wrapper — reuses the existing collection, no rebuild
    _vectorstore = Chroma(
        client=chroma_client,
        collection_name=settings.collection_name,
        embedding_function=embeddings,
    )

    _retriever = _vectorstore.as_retriever(
        search_kwargs={"k": settings.retriever_k}
    )

    count = _vectorstore._collection.count()
    logger.info(
        "Vector store ready — collection '%s' with %d documents.",
        settings.collection_name,
        count,
    )


def retrieve(question: str, k: int | None = None):
    """
    Retrieve the top-k most relevant documents for *question*.

    Args:
        question: The user's natural-language question.
        k:        Override the default retriever k value (optional).

    Returns:
        list[langchain_core.documents.Document]
    """
    if _retriever is None:
        raise RuntimeError(
            "Vector store has not been loaded yet. "
            "Ensure load_vector_store() is called at startup."
        )

    retriever = _retriever
    if k is not None:
        retriever = _vectorstore.as_retriever(search_kwargs={"k": k})

    docs = retriever.invoke(question)
    logger.debug("Retrieved %d docs for query: %r", len(docs), question[:80])
    return docs
