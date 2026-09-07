"""
ElevenLabs Text-to-Speech (TTS) integration.
Synthesizes text to natural-sounding audio using ElevenLabs API.
"""

import logging
import aiohttp
from typing import Optional

logger = logging.getLogger(__name__)


class ElevenLabsTTS:
    """
    ElevenLabs TTS service for synthesizing natural speech.
    Uses REST API directly for compatibility.
    
    Features:
    - Natural-sounding voices
    - Adjustable stability and similarity_boost parameters
    - Multiple voice models available
    """
    
    # Predefined voice IDs (ElevenLabs includes these)
    VOICES = {
        "rachel": "21m00Tcm4TlvDq8ikWAM",      # Female, friendly
        "domi": "AZnzlk1XvdvUBZ4xNXEN",       # Male, strong
        "bella": "EXAVITQu4vr4xnSDxMaL",      # Female, warm
        "elli": "MF3mGyEYCHltNXjT02xQ",      # Female, expressive
        "josh": "TxGEqnHWrfWFTfGW9XjX",      # Male, deep
        "arnold": "VR6AewLHbNrXmDARePnA",    # Male, authoritative
    }
    
    BASE_URL = "https://api.elevenlabs.io/v1"
    
    def __init__(self, api_key: str, voice_id: str = "rachel"):
        """
        Initialize ElevenLabs TTS client.
        
        Args:
            api_key: ElevenLabs API key
            voice_id: Voice ID or name (see VOICES dict)
        """
        self.api_key = api_key
        
        # Resolve voice ID if name is provided
        if voice_id in self.VOICES:
            self.voice_id = self.VOICES[voice_id]
        else:
            self.voice_id = voice_id
        
        logger.info(f"[ElevenLabs] Initialized with voice_id: {self.voice_id}")
    
    async def synthesize(
        self,
        text: str,
        stability: float = 0.5,
        similarity_boost: float = 0.75,
    ) -> bytes:
        """
        Synthesize text to speech using ElevenLabs API.
        
        Args:
            text: Text to synthesize
            stability: Voice stability (0.0-1.0, default 0.5)
            similarity_boost: Similarity to voice (0.0-1.0, default 0.75)
        
        Returns:
            Audio bytes (mp3 format)
        """
        try:
            url = f"{self.BASE_URL}/text-to-speech/{self.voice_id}"
            
            headers = {
                "xi-api-key": self.api_key,
                "Content-Type": "application/json"
            }
            
            data = {
                "text": text,
                "model_id": "eleven_multilingual_v2",
                "voice_settings": {
                    "stability": stability,
                    "similarity_boost": similarity_boost
                }
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=data, headers=headers) as response:
                    if response.status == 200:
                        audio_bytes = await response.read()
                        logger.info(f"[ElevenLabs] Synthesized {len(text)} chars → {len(audio_bytes)} bytes")
                        return audio_bytes
                    else:
                        error = await response.text()
                        logger.error(f"[ElevenLabs] API error: {response.status} - {error}")
                        raise Exception(f"ElevenLabs API error: {response.status}")
        
        except Exception as e:
            logger.error(f"[ElevenLabs] Synthesis failed: {e}")
            raise


async def synthesize_speech(
    api_key: str,
    text: str,
    voice_id: str = "rachel"
) -> bytes:
    """
    Convenience function to synthesize speech.
    
    Args:
        api_key: ElevenLabs API key
        text: Text to synthesize
        voice_id: Voice ID or name
    
    Returns:
        Audio bytes (mp3 format)
    """
    tts = ElevenLabsTTS(api_key, voice_id)
    return await tts.synthesize(text)
