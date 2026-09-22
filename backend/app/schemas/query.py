"""
Pydantic request / response schemas for the /query endpoint.
"""

from pydantic import BaseModel, Field


class QueryRequest(BaseModel):
    """Payload sent by the client to ask a question."""

    question: str = Field(
        ...,
        min_length=3,
        max_length=1000,
        description="The natural-language question to answer.",
        examples=["What is the capital of Uruguay?"],
    )


class QueryResponse(BaseModel):
    """Payload returned by the API after running the RAG pipeline."""

    answer: str = Field(..., description="The grounded answer produced by the LLM.")
    sources: list[str] = Field(
        default_factory=list,
        description="List of source document snippets used to build the answer.",
    )
    blocked: bool = Field(
        default=False,
        description="True when the safety guardrail blocked the request.",
    )
