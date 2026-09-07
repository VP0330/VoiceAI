"""
Pydantic schemas for analysis requests, responses, and insight models.
"""
from typing import Literal, Optional
from pydantic import BaseModel, Field
from datetime import datetime


class Insight(BaseModel):
    """A single extracted insight from the transcript."""
    theme: str = Field(..., description="Main topic or theme")
    quote: str = Field(..., description="Verbatim quote from transcript supporting this theme")
    sentiment: Literal["positive", "neutral", "negative"] = Field(..., description="Sentiment of this insight")
    actionable: bool = Field(..., description="Whether this insight suggests an action")
    recommendation: Optional[str] = Field(None, description="Recommended action, if any")


class LLMCallMetadata(BaseModel):
    """Metadata about a single LLM call for observability."""
    latency_ms: int = Field(..., description="Response latency in milliseconds")
    retry_count: int = Field(..., description="Number of retries before success")
    input_tokens: int = Field(..., description="Tokens consumed by prompt")
    output_tokens: int = Field(..., description="Tokens generated in response")
    total_tokens: int = Field(..., description="Total tokens (input + output)")


class AnalysisRequest(BaseModel):
    """Request to analyze a transcript."""
    transcript: str = Field(..., description="Raw transcript text to analyze")
    session_id: Optional[str] = Field(None, description="Optional session ID; auto-generated if missing")


class AnalysisResponse(BaseModel):
    """Response from transcript analysis."""
    session_id: str = Field(..., description="Session ID for this analysis")
    insights: list[Insight] = Field(..., description="Extracted insights")
    llm_call_metadata: LLMCallMetadata = Field(..., description="Metadata about the LLM call")
    created_at: datetime = Field(..., description="Timestamp of analysis")
