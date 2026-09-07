"""
Voice processing endpoints for Phase 2 - Pipecat integration.
Handles audio input, voice agent processing, and TTS responses.
"""

from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional
import logging
import base64
import os
import json
from uuid import uuid4
from pathlib import Path
from voice.pipecat_agent import create_voice_agent
from db.schema import get_db_connection, return_connection

router = APIRouter(prefix="/api/voice", tags=["voice"])
logger = logging.getLogger(__name__)


class VoiceSessionRequest(BaseModel):
    """Request to create or start voice session"""
    session_id: Optional[str] = None  # Optional; will be generated if not provided


class VoiceAudioRequest(BaseModel):
    """Request to process audio in a session"""
    session_id: str
    audio_format: str = "wav"  # wav, mp3, ogg, etc.


class VoiceProcessingResponse(BaseModel):
    """Response from voice processing endpoint"""
    session_id: str
    transcript: str
    insights: list
    llm_metadata: dict
    response_text: str
    response_audio_base64: Optional[str] = None  # Base64 encoded audio bytes


@router.post("/session/start")
async def start_voice_session(request: VoiceSessionRequest):
    """
    Start a new voice session.
    
    Returns:
        {
            "session_id": str,
            "websocket_url": "ws://localhost:8000/ws/session/{session_id}"
        }
    """
    session_id = request.session_id or str(uuid4())
    
    logger.info(f"[VoiceAPI] Started voice session: {session_id}")
    
    return {
        "session_id": session_id,
        "websocket_url": f"ws://localhost:8000/ws/session/{session_id}",
        "status": "ready"
    }


@router.post("/process", response_model=VoiceProcessingResponse)
async def process_voice_input(
    session_id: str = Form(...),
    audio_file: UploadFile = File(...)
):
    """
    Process voice input (audio file).
    
    1. Transcribe audio (Deepgram STT)
    2. Analyze transcript (Ollama LLM)
    3. Generate response (ElevenLabs TTS)
    4. Broadcast via WebSocket
    
    Args:
        session_id: Session ID
        audio_file: Audio file (wav, mp3, ogg, etc.)
    
    Returns:
        {
            "session_id": str,
            "transcript": str,
            "insights": list,
            "llm_metadata": dict,
            "response_text": str,
            "response_audio_base64": str (base64 encoded audio or null)
        }
    """
    try:
        # Read audio data
        audio_data = await audio_file.read()
        logger.info(f"[VoiceAPI] Received {len(audio_data)} bytes of audio for session {session_id}")
        
        # IMPORTANT: Create session first before processing
        from db.schema import save_session
        save_session(session_id)

        # Create voice agent
        agent = await create_voice_agent(session_id)
        
        # Process full voice loop
        result = await agent.process_voice_input(audio_data)
        
        logger.info(f"[VoiceAPI] Processing complete for session {session_id}")
        
        # Save response text to session folder for later audio generation
        session_output_dir = Path("audio_outputs") / session_id
        session_output_dir.mkdir(parents=True, exist_ok=True)
        
        # Save response text
        response_file = session_output_dir / "response.txt"
        with open(response_file, "w") as f:
            f.write(result["response_text"])
        logger.info(f"[VoiceAPI] Saved response text to {response_file}")
        
        # Save metadata for reference
        metadata_file = session_output_dir / "metadata.json"
        metadata = {
            "session_id": session_id,
            "transcript": result["transcript"],
            "response_text": result["response_text"],
            "llm_metadata": result["llm_metadata"],
            "insights": result["insights"]
        }
        with open(metadata_file, "w") as f:
            json.dump(metadata, f, indent=2)
        logger.info(f"[VoiceAPI] Saved metadata to {metadata_file}")
        
        # Encode audio response as base64 if available (currently None)
        response_audio_base64 = None
        if result.get("response_audio"):
            response_audio_base64 = base64.b64encode(result["response_audio"]).decode('utf-8')
        
        return VoiceProcessingResponse(
            session_id=result["session_id"],
            transcript=result["transcript"],
            insights=result["insights"],
            llm_metadata=result["llm_metadata"],
            response_text=result["response_text"],
            response_audio_base64=response_audio_base64
        )
    
    except Exception as e:
        logger.error(f"[VoiceAPI] Error processing voice: {e}")
        raise HTTPException(status_code=500, detail=f"Voice processing failed: {str(e)}")


@router.get("/session/{session_id}/status")
async def get_session_status(session_id: str):
    """
    Get status of a voice session.
    
    Returns:
        {
            "session_id": str,
            "status": "active" | "completed" | "error",
            "transcript": str,
            "insights_count": int
        }
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Check if session exists
        cursor.execute("SELECT id FROM sessions WHERE id = %s", (session_id,))
        session = cursor.fetchone()
        
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Count transcript turns
        cursor.execute("SELECT COUNT(*) FROM transcript_turns WHERE session_id = %s", (session_id,))
        transcript_count = cursor.fetchone()[0]
        
        # Count insights
        cursor.execute("SELECT COUNT(*) FROM insights WHERE session_id = %s", (session_id,))
        insights_count = cursor.fetchone()[0]
        
        # Get aggregated transcript
        cursor.execute(
            "SELECT COALESCE(string_agg(text, ' '), '') FROM transcript_turns WHERE session_id = %s ORDER BY timestamp_ms",
            (session_id,)
        )
        transcript_result = cursor.fetchone()
        transcript_text = transcript_result[0] if transcript_result else ""
        
        # Determine status (active if has data, otherwise completed)
        status = "active" if transcript_count > 0 else "completed"
        
        return {
            "session_id": session_id,
            "status": status,
            "transcript": transcript_text,
            "insights_count": insights_count
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[VoiceAPI] Error getting session status: {e}")
        raise HTTPException(status_code=500, detail="Failed to get session status")
    finally:
        cursor.close()
        return_connection(conn)


@router.get("/sessions")
async def list_sessions():
    """
    Get list of all sessions with their status and insight counts.
    
    Returns:
        [
            {
                "session_id": str,
                "status": "active" | "completed" | "error",
                "transcript": str,
                "insights_count": int,
                "created_at": datetime
            },
            ...
        ]
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Get all sessions with their metadata
        cursor.execute("""
            SELECT 
                s.id,
                s.created_at,
                COUNT(DISTINCT t.id) as transcript_count,
                COUNT(DISTINCT i.id) as insights_count
            FROM sessions s
            LEFT JOIN transcript_turns t ON s.id = t.session_id
            LEFT JOIN insights i ON s.id = i.session_id
            GROUP BY s.id, s.created_at
            ORDER BY s.created_at DESC
            LIMIT 100
        """)
        
        sessions = cursor.fetchall()
        result = []
        
        for session_row in sessions:
            session_id, created_at, transcript_count, insights_count = session_row
            
            # Get aggregated transcript for each session
            cursor.execute(
                "SELECT COALESCE(string_agg(text, ' '), '') FROM transcript_turns WHERE session_id = %s ORDER BY timestamp_ms LIMIT 1",
                (session_id,)
            )
            transcript_result = cursor.fetchone()
            transcript_text = transcript_result[0] if transcript_result else ""
            
            # Determine status
            status = "active" if transcript_count > 0 else "completed"
            
            result.append({
                "session_id": session_id,
                "status": status,
                "transcript": transcript_text[:200],  # Truncate for display
                "insights_count": insights_count or 0,
                "created_at": created_at.isoformat() if created_at else None
            })
        
        return result
    
    except Exception as e:
        logger.error(f"[VoiceAPI] Error listing sessions: {e}")
        raise HTTPException(status_code=500, detail="Failed to list sessions")
    finally:
        cursor.close()
        return_connection(conn)


@router.post("/session/{session_id}/generate-audio")
async def generate_session_audio(session_id: str, voice_id: str = "default"):
    """
    Generate audio for a session's response text.
    
    This is called on-demand after the main voice processing is complete.
    Reads response.txt from audio_outputs/{session_id}/ and synthesizes to audio.
    
    Args:
        session_id: Session ID
        voice_id: Voice ID for TTS (default uses system default voice)
    
    Returns:
        {
            "session_id": str,
            "status": "generated" | "error",
            "audio_file": str (path to generated audio),
            "message": str
        }
    """
    try:
        session_output_dir = Path("audio_outputs") / session_id
        response_file = session_output_dir / "response.txt"
        
        if not response_file.exists():
            raise HTTPException(
                status_code=404, 
                detail=f"Response text not found for session {session_id}. Run /api/voice/process first."
            )
        
        # Read response text
        with open(response_file, "r") as f:
            response_text = f.read()
        
        logger.info(f"[VoiceAPI] Generating audio for session {session_id}: {response_text[:50]}...")
        
        # Import TTS client here to avoid blocking main request
        from voice.coqui_tts_client import LocalTTS
        
        # Generate audio
        tts = LocalTTS(voice_id=voice_id)
        audio_bytes = await tts.synthesize(response_text)
        
        # Save audio file
        audio_file = session_output_dir / "response_audio.wav"
        with open(audio_file, "wb") as f:
            f.write(audio_bytes)
        
        logger.info(f"[VoiceAPI] Generated audio saved to {audio_file} ({len(audio_bytes)} bytes)")
        
        return {
            "session_id": session_id,
            "status": "generated",
            "audio_file": str(audio_file),
            "message": f"Audio generated: {len(audio_bytes)} bytes"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[VoiceAPI] Error generating audio: {e}")
        raise HTTPException(status_code=500, detail=f"Audio generation failed: {str(e)}")


@router.get("/session/{session_id}/audio")
async def get_session_audio(session_id: str):
    """
    Retrieve generated audio file for a session.
    
    Returns the audio file if it exists, otherwise returns 404.
    """
    try:
        audio_file = Path("audio_outputs") / session_id / "response_audio.wav"
        
        if not audio_file.exists():
            raise HTTPException(
                status_code=404, 
                detail=f"Audio not found for session {session_id}. Call /api/voice/session/{session_id}/generate-audio first."
            )
        
        # Return file with proper headers for audio streaming
        return FileResponse(
            audio_file,
            media_type="audio/wav",
            filename=f"{session_id}_response.wav"
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[VoiceAPI] Error retrieving audio: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve audio: {str(e)}")
