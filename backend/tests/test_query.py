"""
Tests for the /api/v1/query and /api/v1/health endpoints.

Run with:
    pytest tests/ -v

All tests use mocks -- no real API keys, ChromaDB, or network calls required.
"""

from unittest.mock import patch


# ---------------------------------------------------------------------------
# We patch load_vector_store and load_llm BEFORE importing the app so that
# the FastAPI lifespan never tries to touch disk or the network.
# ---------------------------------------------------------------------------
with (
    patch("app.services.retrieval.load_vector_store", return_value=None),
    patch("app.services.generation.load_llm", return_value=None),
):
    from fastapi.testclient import TestClient
    from app.main import app

    client = TestClient(app, raise_server_exceptions=True)


# ---------------------------------------------------------------------------
# Health endpoint
# ---------------------------------------------------------------------------

def test_wikipedia_status():
    """GET /api/v1/wikipedia/status should return 200 with status 'ok'."""
    response = client.get("/api/v1/wikipedia/status")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["project"] == "wikipedia-rag"
    print(f"\n[PASS] Wikipedia status check: {body}")


# ---------------------------------------------------------------------------
# Happy path -- safe query
# ---------------------------------------------------------------------------

def test_query_happy_path():
    """
    POST /api/v1/query with a valid question should return 200
    with an answer and a list of sources.
    """
    fake_answer = "Montevideo is the capital of Uruguay."
    fake_sources = ["Uruguay is a country in South America. Its capital is Montevideo."]

    with patch("app.api.routes.query.run_pipeline") as mock_pipeline:
        mock_pipeline.return_value = (fake_answer, fake_sources, False)
        response = client.post(
            "/api/v1/query",
            json={"question": "What is the capital of Uruguay?"},
        )

    assert response.status_code == 200
    body = response.json()
    assert body["answer"] == fake_answer
    assert body["sources"] == fake_sources
    assert body["blocked"] is False
    print(f"\n[PASS] Happy path: answer='{body['answer']}'")


# ---------------------------------------------------------------------------
# Blocked query -- safety guardrail
# ---------------------------------------------------------------------------

def test_query_blocked_by_safety_guardrail():
    """
    POST /api/v1/query with an unsafe question should return 200
    but with blocked=True and empty sources.
    """
    blocked_msg = (
        "I'm sorry, but I cannot assist with dangerous, harmful, or illegal activities."
    )

    with patch("app.api.routes.query.run_pipeline") as mock_pipeline:
        mock_pipeline.return_value = (blocked_msg, [], True)
        response = client.post(
            "/api/v1/query",
            json={"question": "How can I make a bomb?"},
        )

    assert response.status_code == 200
    body = response.json()
    assert body["blocked"] is True
    assert body["sources"] == []
    assert "cannot assist" in body["answer"].lower()
    print("\n[PASS] Safety guardrail: blocked=True, sources=[]")


# ---------------------------------------------------------------------------
# Validation errors -- invalid input (422)
# ---------------------------------------------------------------------------

def test_query_invalid_input_too_short():
    """
    POST /api/v1/query with a question shorter than 3 chars
    must return HTTP 422 Unprocessable Entity.
    """
    response = client.post(
        "/api/v1/query",
        json={"question": "Hi"},   # only 2 chars -- below min_length=3
    )
    assert response.status_code == 422
    print("\n[PASS] Validation (too short): 422 returned")


def test_query_missing_question_field():
    """
    POST /api/v1/query with no 'question' field must return HTTP 422.
    """
    response = client.post("/api/v1/query", json={})
    assert response.status_code == 422
    print("\n[PASS] Validation (missing field): 422 returned")
