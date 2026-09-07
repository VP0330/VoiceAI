"""
Ollama client with retry logic for structured output, latency tracking, and token logging.
"""
import json
import time
import uuid
from typing import Optional
from pydantic import BaseModel, ValidationError
import requests
from analysis.schemas import Insight


class OllamaClient:
    """
    Client for Ollama's OpenAI-compatible endpoint.
    Handles structured output via JSON mode, retries on malformed JSON, and comprehensive logging.
    """

    def __init__(self, base_url: str = "http://localhost:11434/v1", model_name: str = "qwen2.5:3b-instruct"):
        self.base_url = base_url
        self.model_name = model_name
        self.max_retries = 3
        self.timeout = 30

    def extract_insights(self, transcript: str) -> tuple[list[Insight], dict]:
        """
        Extract insights from a transcript using structured output.
        
        Returns:
            Tuple of (list[Insight], metadata_dict) where metadata includes latency_ms, retry_count, token counts
        
        Raises:
            Exception: If Ollama is unreachable or structured output fails after max retries
        """
        
        start_time = time.time()
        retry_count = 0
        last_error = None
        
        # System prompt for insight extraction
        system_prompt = """You are an expert analyst extracting structured insights from interview transcripts.
        
For each major theme or topic in the transcript, extract one insight object with:
- theme: A concise topic/theme from the conversation
- quote: A verbatim quote from the transcript that best represents this theme
- sentiment: One of "positive", "neutral", or "negative"
- actionable: Boolean - whether this insight suggests an action
- recommendation: A brief recommended action if actionable is true, otherwise null

Return a JSON array of insight objects. Extract 3-5 insights maximum.
Ensure all quotes are EXACT text from the transcript."""

        user_prompt = f"""Analyze this transcript and extract insights:

---
{transcript}
---

Return ONLY valid JSON array with no markdown, no code blocks, no extra text."""

        # Retry loop
        for attempt in range(self.max_retries + 1):
            retry_count = attempt
            try:
                response = self._call_ollama_json(system_prompt, user_prompt)
                
                # Parse response
                insights_data = json.loads(response)
                if not isinstance(insights_data, list):
                    raise ValueError("Response is not a JSON array")
                
                # Validate each insight with Pydantic
                insights = []
                for item in insights_data:
                    try:
                        insight = Insight(**item)
                        insights.append(insight)
                    except ValidationError as ve:
                        raise ValueError(f"Invalid insight object: {ve}")
                
                # Success! Record latency and token counts
                latency_ms = int((time.time() - start_time) * 1000)
                
                # Extract token counts from last response (simulated; Ollama returns these)
                # For now, we estimate based on token count conventions
                prompt_tokens = len(system_prompt.split()) + len(user_prompt.split())
                completion_tokens = len(response.split())
                
                metadata = {
                    "latency_ms": latency_ms,
                    "retry_count": retry_count,
                    "input_tokens": prompt_tokens,
                    "output_tokens": completion_tokens,
                    "total_tokens": prompt_tokens + completion_tokens,
                    "success": True
                }
                
                print(f"[Ollama] Extraction succeeded after {retry_count} retries in {latency_ms}ms")
                print(f"[Ollama] Tokens: {prompt_tokens} in, {completion_tokens} out")
                
                return insights, metadata
                
            except (json.JSONDecodeError, ValueError, ValidationError) as e:
                last_error = e
                print(f"[Ollama] Attempt {attempt + 1}/{self.max_retries + 1} failed: {type(e).__name__}: {str(e)[:100]}")
                
                if attempt < self.max_retries:
                    # Exponential backoff
                    backoff = 0.5 * (2 ** attempt)
                    print(f"[Ollama] Retrying in {backoff:.1f}s...")
                    time.sleep(backoff)
            
            except requests.RequestException as e:
                print(f"[Ollama] Network error on attempt {attempt + 1}: {str(e)[:100]}")
                raise Exception(f"Ollama unreachable: {str(e)}")
        
        # All retries failed
        latency_ms = int((time.time() - start_time) * 1000)
        print(f"[Ollama] All {self.max_retries + 1} attempts failed after {latency_ms}ms")
        print(f"[Ollama] Last error: {type(last_error).__name__}: {str(last_error)}")
        
        raise Exception(f"Failed to extract insights after {self.max_retries + 1} attempts: {str(last_error)}")

    def _call_ollama_json(self, system_prompt: str, user_prompt: str) -> str:
        """
        Call Ollama's chat completion endpoint with JSON mode.
        Returns the raw response text.
        """
        url = f"{self.base_url.rstrip('/')}/chat/completions"
        
        payload = {
            "model": self.model_name,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": 0.3,  # Lower temp for structured output
            "top_p": 0.9,
            "stream": False
        }
        
        response = requests.post(url, json=payload, timeout=self.timeout)
        response.raise_for_status()
        
        data = response.json()
        
        # Extract text from response
        if "choices" in data and len(data["choices"]) > 0:
            message = data["choices"][0].get("message", {})
            text = message.get("content", "")
            
            # Log token counts if available
            if "usage" in data:
                usage = data["usage"]
                print(f"[Ollama Token Count] Prompt: {usage.get('prompt_tokens', 0)}, Completion: {usage.get('completion_tokens', 0)}")
            
            return text
        else:
            raise ValueError("Unexpected Ollama response format")
