"""
Voice agent for Phase 2.
Handles real-time STT (Deepgram), analysis (Ollama), and TTS (Coqui local).
"""

import os
import json
import asyncio
import logging
from uuid import uuid4
from typing import Optional, Callable
from dataclasses import dataclass

# Local imports
from analysis.ollama_client import OllamaClient
from db.schema import get_db_connection, save_insights
from voice.deepgram_client import DeepgramSTT
from voice.coqui_tts_client import LocalTTS

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class VoiceAgentConfig:
    """Configuration for voice agent"""
    session_id: str
    deepgram_api_key: str
    ollama_base_url: str = "http://localhost:11434/v1"
    ollama_model: str = "qwen2.5:3b-instruct"
    language: str = "en"
    voice_id: str = "default"  # Coqui TTS voice


class VoiceAgent:
    """
    Full-loop voice agent:
    1. Record user voice → Deepgram STT → transcript
    2. Send transcript to /api/analyze → insights + metadata
    3. Generate response text → ElevenLabs TTS → play audio
    """
    
    def __init__(self, config: VoiceAgentConfig, on_transcript_turn: Optional[Callable] = None):
        self.config = config
        self.ollama_client = OllamaClient(config.ollama_base_url, config.ollama_model)
        self.on_transcript_turn = on_transcript_turn  # Callback for WebSocket broadcasting
        self.accumulated_transcript = ""
        
        logger.info(f"[VoiceAgent] Initialized with session_id: {config.session_id}")
    
    async def process_voice_input(self, audio_data: bytes) -> dict:
        """
        Full voice loop:
        1. STT on audio_data
        2. Extract insights via Ollama
        3. Generate TTS response
        
        Returns:
            {
                "session_id": str,
                "transcript": str,
                "insights": list,
                "llm_metadata": dict,
                "response_audio": bytes (if TTS enabled)
            }
        """
        try:
            # Step 1: Speech-to-Text (Deepgram)
            transcript = await self._transcribe_audio(audio_data)
            logger.info(f"[VoiceAgent] Transcribed: {transcript}")
            
            # Broadcast transcript turn via WebSocket if callback provided
            if self.on_transcript_turn:
                await self.on_transcript_turn(
                    session_id=self.config.session_id,
                    speaker="user",
                    text=transcript,
                    timestamp_ms=0
                )
            
            # Step 2: Analyze with Ollama (using existing client)
            insights, llm_metadata = self.ollama_client.extract_insights(transcript)
            logger.info(f"[VoiceAgent] Extracted {len(insights)} insights")
            
            # Save to database (run in thread pool to avoid blocking event loop)
            await asyncio.to_thread(self._save_to_database, transcript, insights, llm_metadata)
            
            # Step 3: Generate response text (from insights)
            response_text = self._generate_response(insights)
            logger.info(f"[VoiceAgent] Generated response: {response_text}")
            
            # Step 4: Text-to-Speech (SKIPPED)
            # Audio synthesis is now deferred - will be generated on-demand or stored separately
            logger.info(f"[VoiceAgent] Skipping TTS synthesis - audio will be generated on-demand")
            
            # Broadcast agent response via WebSocket
            if self.on_transcript_turn:
                await self.on_transcript_turn(
                    session_id=self.config.session_id,
                    speaker="agent",
                    text=response_text,
                    timestamp_ms=0
                )
            
            return {
                "session_id": self.config.session_id,
                "transcript": transcript,
                "insights": [i.model_dump() for i in insights],
                "llm_metadata": llm_metadata,
                "response_text": response_text,
                "response_audio": None
            }
        
        except Exception as e:
            logger.error(f"[VoiceAgent] Error: {e}")
            raise
    
    async def _transcribe_audio(self, audio_data: bytes) -> str:
        """
        Transcribe audio using Deepgram.
        """
        try:
            stt = DeepgramSTT(self.config.deepgram_api_key)
            result = await stt.transcribe(audio_data)
            transcript = result["transcript"]
            logger.info(f"[VoiceAgent] Transcribed audio: {transcript[:100]}...")
            return transcript
        except Exception as e:
            logger.error(f"[VoiceAgent] Transcription failed: {e}")
            raise
    
    async def _synthesize_speech(self, text: str) -> bytes:
        """
        Synthesize speech using pyttsx3 (local, no API key needed).
        NOTE: Currently deferred - can be called on-demand via separate endpoint.
        """
        try:
            tts = LocalTTS(voice_id=self.config.voice_id)
            audio_bytes = await tts.synthesize(text)
            logger.info(f"[VoiceAgent] Synthesized speech: {len(audio_bytes)} bytes")
            return audio_bytes
        except Exception as e:
            logger.error(f"[VoiceAgent] Speech synthesis failed: {e}")
            raise
    
    def _generate_response(self, insights: list) -> str:
        """Generate conversational response from insights"""
        if not insights:
            return "I couldn't extract any insights from that. Could you tell me more?"
        
        # Build response from insights
        themes = [i.theme for i in insights]
        themes_str = ", ".join(themes[:2])  # First 2 themes
        
        response = f"I noticed some key themes: {themes_str}. "
        
        # Add recommendations if available
        recommendations = [i.recommendation for i in insights if i.recommendation]
        if recommendations:
            response += f"Here's my suggestion: {recommendations[0]}"
        
        return response
    
    def _save_to_database(self, transcript: str, insights: list, llm_metadata: dict):
        """Save transcript, insights, and LLM call metadata to PostgreSQL"""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # Save transcript turn with generated UUID
            turn_id = str(uuid4())
            cursor.execute("""
                INSERT INTO transcript_turns (id, session_id, speaker, text, timestamp_ms, created_at)
                VALUES (%s, %s, %s, %s, %s, NOW())
            """, (turn_id, self.config.session_id, "user", transcript, 0))
            
            # Save LLM call metadata with generated UUID
            llm_call_id = str(uuid4())
            cursor.execute("""
                INSERT INTO llm_calls (
                    id, session_id, prompt, response, latency_ms, retry_count,
                    input_tokens, output_tokens, total_tokens, success, created_at
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW())
            """, (
                llm_call_id,
                self.config.session_id,
                transcript,
                json.dumps([i.model_dump() for i in insights]),
                llm_metadata.get('latency_ms', 0),
                llm_metadata.get('retry_count', 0),
                llm_metadata.get('input_tokens', 0),
                llm_metadata.get('output_tokens', 0),
                llm_metadata.get('total_tokens', 0),
                True
            ))
            
            # Save insights
            insight_dicts = [
                {
                    'id': str(uuid4()),
                    'theme': i.theme,
                    'quote': i.quote,
                    'sentiment': i.sentiment,
                    'actionable': i.actionable,
                    'recommendation': i.recommendation
                }
                for i in insights
            ]
            save_insights(self.config.session_id, insight_dicts)
            
            conn.commit()
            conn.close()
            logger.info("[VoiceAgent] Saved to database")
        
        except Exception as e:
            logger.error(f"[VoiceAgent] Database save failed: {e}")
            raise


async def create_voice_agent(
    session_id: str,
    on_transcript_turn: Optional[Callable] = None
) -> VoiceAgent:
    """Factory function to create voice agent with env config"""
    # Validate required environment variables
    deepgram_api_key = os.getenv("DEEPGRAM_API_KEY")
    if not deepgram_api_key:
        raise ValueError("DEEPGRAM_API_KEY environment variable is not set")
    
    config = VoiceAgentConfig(
        session_id=session_id,
        deepgram_api_key=deepgram_api_key,
        ollama_base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434/v1"),
        ollama_model=os.getenv("OLLAMA_MODEL", "qwen2.5:3b-instruct"),
        voice_id=os.getenv("TTS_VOICE_ID", "default"),  # TTS voice (pyttsx3)
    )
    return VoiceAgent(config, on_transcript_turn)
