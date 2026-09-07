"""
pyttsx3 Text-to-Speech (TTS) integration.
Synthesizes text to natural-sounding audio using pyttsx3 (system voices).
No API key required - runs completely offline using system TTS engine.
"""

import asyncio
import io
import logging
import tempfile
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

# Lazy import to avoid initialization overhead
_engine_instance = None

def _get_engine():
    """Lazy load pyttsx3 engine to avoid startup overhead."""
    global _engine_instance
    if _engine_instance is None:
        try:
            import pyttsx3
            _engine_instance = pyttsx3.init()
            logger.info("[TTS] pyttsx3 engine initialized")
        except ImportError:
            logger.error("[TTS] pyttsx3 not installed. Run: pip install pyttsx3")
            raise
        except Exception as e:
            logger.error(f"[TTS] Engine initialization failed: {e}")
            raise
    return _engine_instance


class LocalTTS:
    """
    Local TTS service using system voices via pyttsx3.
    No API key required - runs completely offline.
    
    Features:
    - Uses system TTS engine (Windows SAPI, macOS NSSpeechSynthesizer, Linux espeak)
    - Multiple voices available
    - Runs locally with zero cost
    - Fast synthesis
    """
    
    def __init__(self, voice_id: str = "default"):
        """
        Initialize local TTS client.
        
        Args:
            voice_id: Voice name or index (default uses first available voice)
        """
        self.voice_id = voice_id
        logger.info(f"[TTS] Initialized with voice_id: {self.voice_id}")
    
    async def synthesize(
        self,
        text: str,
        speed: float = 1.0,
    ) -> bytes:
        """
        Synthesize text to speech using pyttsx3.
        
        Args:
            text: Text to synthesize
            speed: Speaking speed (0.5-2.0, default 1.0)
        
        Returns:
            Audio bytes (WAV format)
        """
        try:
            # Run TTS in thread pool to avoid blocking async event loop
            loop = asyncio.get_event_loop()
            audio_bytes = await loop.run_in_executor(
                None,
                self._synthesize_blocking,
                text,
                speed
            )
            logger.info(f"[TTS] Synthesized {len(text)} chars → {len(audio_bytes)} bytes")
            return audio_bytes
        except Exception as e:
            logger.error(f"[TTS] Synthesis failed: {e}")
            raise
    
    def _synthesize_blocking(self, text: str, speed: float) -> bytes:
        """
        Blocking synthesis (runs in executor thread).
        pyttsx3's synthesize() is synchronous, so we run it in a thread pool.
        """
        engine = _get_engine()
        
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
            tmp_path = tmp.name
        
        try:
            # Set speech rate (pyttsx3 default is ~200 WPM)
            engine.setProperty('rate', int(200 * speed))
            
            # Try to set voice if voice_id is numeric (voice index)
            try:
                voices = engine.getProperty('voices')
                voice_idx = int(self.voice_id) if self.voice_id != "default" else 0
                if 0 <= voice_idx < len(voices):
                    engine.setProperty('voice', voices[voice_idx].id)
            except (ValueError, IndexError):
                pass  # Use default voice
            
            # Save to file and read back as bytes
            engine.save_to_file(text, tmp_path)
            engine.runAndWait()
            
            # Read file as bytes
            with open(tmp_path, "rb") as f:
                audio_bytes = f.read()
            
            return audio_bytes
        finally:
            # Clean up temp file
            Path(tmp_path).unlink(missing_ok=True)


async def synthesize_speech(
    text: str,
    voice_id: str = "default",
    speed: float = 1.0
) -> bytes:
    """
    Convenience function to synthesize speech.
    
    Args:
        text: Text to synthesize
        voice_id: Voice ID or name (default uses system default voice)
        speed: Speaking speed (0.5-2.0, default 1.0)
    
    Returns:
        Audio bytes (WAV format)
    """
    tts = LocalTTS(voice_id)
    return await tts.synthesize(text, speed)
