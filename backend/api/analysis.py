"""
FastAPI endpoint for transcript analysis.
"""
import uuid
import json
from datetime import datetime
from fastapi import APIRouter, HTTPException
from analysis.schemas import AnalysisRequest, AnalysisResponse, LLMCallMetadata, Insight
from analysis.ollama_client import OllamaClient
from db.schema import save_session, save_llm_call, save_insights

router = APIRouter(prefix="/api", tags=["analysis"])
ollama_client = OllamaClient()


@router.post("/analyze", response_model=AnalysisResponse)
async def analyze_transcript(request: AnalysisRequest):
    """
    Analyze a transcript and extract structured insights.
    
    Request:
        - transcript: Raw transcript text
        - session_id: Optional session ID (auto-generated if not provided)
    
    Response:
        - session_id: Generated/provided session ID
        - insights: List of extracted Insight objects
        - llm_call_metadata: Metadata about the LLM call (latency, retries, tokens)
        - created_at: Timestamp of analysis
    
    Raises:
        - 400: If Ollama is unreachable or structured output fails after retries
        - 500: Unexpected server error
    """
    
    # Generate session ID if not provided
    session_id = request.session_id or str(uuid.uuid4())
    
    try:
        # Save session to DB
        save_session(session_id)
        
        # Call Ollama for insight extraction
        insights, metadata = ollama_client.extract_insights(request.transcript)
        
        # Prepare insight objects for DB storage
        insights_for_db = []
        for insight in insights:
            insights_for_db.append({
                "id": str(uuid.uuid4()),
                "theme": insight.theme,
                "quote": insight.quote,
                "sentiment": insight.sentiment,
                "actionable": insight.actionable,
                "recommendation": insight.recommendation
            })
        
        # Save insights to DB
        save_insights(session_id, insights_for_db)
        
        # Save LLM call metadata to DB
        llm_call_id = f"{session_id}-llm-call"
        save_llm_call(
            session_id=session_id,
            llm_call_id=llm_call_id,
            prompt=f"System: Extract insights from transcript.\nUser: {request.transcript[:500]}...",  # Truncate for logging
            response=json.dumps([i.model_dump() for i in insights]),  # Log structured response
            latency_ms=metadata["latency_ms"],
            retry_count=metadata["retry_count"],
            input_tokens=metadata["input_tokens"],
            output_tokens=metadata["output_tokens"],
            success=True
        )
        
        # Build response
        response = AnalysisResponse(
            session_id=session_id,
            insights=insights,
            llm_call_metadata=LLMCallMetadata(**metadata),
            created_at=datetime.utcnow()
        )
        
        return response
        
    except Exception as e:
        # On error, still try to save the failed LLM call for observability
        try:
            save_llm_call(
                session_id=session_id,
                llm_call_id=f"{session_id}-llm-call-failed",
                prompt=request.transcript[:500],
                response=str(e),
                latency_ms=0,
                retry_count=0,
                input_tokens=0,
                output_tokens=0,
                success=False
            )
        except Exception:
            pass  # Best effort; don't obscure original error
        
        raise HTTPException(status_code=400, detail=f"Analysis failed: {str(e)}")
