"""
Deepgram Speech-to-Text (STT) integration.
Transcribes audio to text using Deepgram API.
"""

import logging
from typing import Optional
from deepgram import DeepgramClient

logger = logging.getLogger(__name__)


class DeepgramSTT:
    """
    Deepgram STT service for transcribing audio.
    
    Features:
    - Supports multiple audio formats (wav, mp3, ogg, flac)
    - Multi-language support
    - Confidence scores
    - Word-level timing
    """
    
    def __init__(self, api_key: str):
        """
        Initialize Deepgram STT client.
        
        Args:
            api_key: Deepgram API key (from env or parameter)
        """
        self.api_key = api_key
        self.client = DeepgramClient(api_key=api_key)
    
    async def transcribe(
        self,
        audio_data: bytes,
        audio_format: str = "wav",
        language: str = "en",
        model: str = "nova-2"
    ) -> dict:
        """
        Transcribe audio to text.
        """
        try:
            # Import PrerecordedOptions inside method to avoid import issues
            from deepgram.clients import PrerecordedOptions
            
            # Create options object
            options = PrerecordedOptions(
                model=model,
                language=language,
                smart_format=True,
                punctuate=True
            )
            
            payload = {"buffer": audio_data}
            
            # FIXED: .v("1") is a method call (returns the versioned client),
            # NOT an attribute (.v1). And we need `asyncprerecorded`, not
            # `prerecorded`, to get an awaitable call.
            response = await self.client.listen.asyncprerecorded.v("1").transcribe_file(
                payload,
                options
            )
            
            # Extract transcript
            if response and response.results:
                # Safely extract transcript with validation
                if not response.results.channels or len(response.results.channels) == 0:
                    logger.warning("[Deepgram] No channels in response")
                    return {
                        "transcript": "",
                        "confidence": 0.0,
                        "duration": 0.0,
                        "words": []
                    }
                
                channel = response.results.channels[0]
                if not channel.alternatives or len(channel.alternatives) == 0:
                    logger.warning("[Deepgram] No alternatives in channel")
                    return {
                        "transcript": "",
                        "confidence": 0.0,
                        "duration": 0.0,
                        "words": []
                    }
                
                alternative = channel.alternatives[0]
                transcript = alternative.transcript
                confidence = alternative.confidence
                duration = response.metadata.duration
                
                logger.info(f"[Deepgram] Transcribed: {transcript[:50]}... (confidence: {confidence})")
                
                return {
                    "transcript": transcript,
                    "confidence": confidence,
                    "duration": duration,
                    "words": []
                }
            else:
                logger.warning("[Deepgram] No transcript returned")
                return {
                    "transcript": "",
                    "confidence": 0.0,
                    "duration": 0.0,
                    "words": []
                }
        
        except Exception as e:
            logger.error(f"[Deepgram] Transcription failed: {e}")
            raise


async def transcribe_audio(
    api_key: str,
    audio_data: bytes,
    audio_format: str = "wav"
) -> str:
    """
    Convenience function to transcribe audio.
    
    Args:
        api_key: Deepgram API key
        audio_data: Raw audio bytes
        audio_format: Audio format
    
    Returns:
        Transcript text
    """
    stt = DeepgramSTT(api_key)
    result = await stt.transcribe(audio_data, audio_format)
    return result["transcript"]
    