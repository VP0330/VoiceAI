# Voice-to-Insight Backend — Phase 1 Setup Guide

## Prerequisites

1. **Python 3.11+** installed
2. **Ollama** installed and running with `qwen2.5:3b-instruct` model
3. **pip** for dependency installation

---

## Installation & Setup

### Step 1: Install Ollama (One-time, Manual)

1. Download Ollama from https://ollama.com
2. Run the Windows installer and follow prompts
3. Restart your terminal/PowerShell
4. Verify installation:
   ```powershell
   ollama --version
   ```

### Step 2: Pull the Qwen2.5-3B-Instruct Model

```powershell
ollama pull qwen2.5:3b-instruct
```

**Notes:**
- This downloads ~2 GB of model weights
- Requires ~3–4 GB RAM to run comfortably
- Model auto-starts on first API call; subsequent calls reuse the running instance
- You can check running models with: `ollama list`

### Step 3: Verify Ollama Endpoint is Reachable

In PowerShell, test the OpenAI-compatible endpoint:

```powershell
curl http://localhost:11434/v1/models
```

You should see a JSON response listing available models including `qwen2.5:3b-instruct`.

### Step 4: Install Python Dependencies

From the `backend/` directory:

```powershell
pip install -r requirements.txt
```

### Step 5: Create `.env` File (Optional)

Copy `.env.example` to `.env` and customize if needed:

```powershell
Copy-Item .env.example .env
```

Default settings point to `http://localhost:11434/v1` (Ollama local endpoint).

---

## Running the Backend Server

From the `backend/` directory:

```powershell
python -m uvicorn main:app --reload --port 8000
```

You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete
INFO:     Database ready
```

The API will be available at `http://localhost:8000`.

---

## Testing Phase 1

### Test 1: Health Check

```powershell
curl http://localhost:8000/health
```

Expected response:
```json
{"status":"ok","service":"voice-to-insight"}
```

### Test 2: Analyze a Transcript (Structured Output Test)

Create a file `test_request.json`:

```json
{
  "transcript": "Interviewer: Tell me about your biggest challenge at work. Interviewee: Time management is tough. I have five projects running in parallel, and it's hard to prioritize. I found that blocking time on calendar helps a lot. Interviewer: That sounds effective. Any other strategies? Interviewee: Yes, I use daily standups with my team to stay aligned. It reduces back-and-forth communication.",
  "session_id": "test-session-001"
}
```

Send the request:

```powershell
$body = Get-Content test_request.json | ConvertFrom-Json | ConvertTo-Json -Compress
curl -X POST "http://localhost:8000/api/analyze" -H "Content-Type: application/json" -d $body
```

**Expected response** (sample):
```json
{
  "session_id": "test-session-001",
  "insights": [
    {
      "theme": "Time Management Challenge",
      "quote": "Time management is tough. I have five projects running in parallel",
      "sentiment": "neutral",
      "actionable": true,
      "recommendation": "Implement project prioritization framework"
    },
    {
      "theme": "Effective Scheduling Technique",
      "quote": "I found that blocking time on calendar helps a lot",
      "sentiment": "positive",
      "actionable": true,
      "recommendation": "Document and share calendar blocking practice with team"
    }
  ],
  "llm_call_metadata": {
    "latency_ms": 1234,
    "retry_count": 0,
    "input_tokens": 156,
    "output_tokens": 89,
    "total_tokens": 245
  },
  "created_at": "2026-09-07T12:34:56"
}
```

**Check the terminal logs** for:
- `[Ollama] Extraction succeeded after X retries`
- Token counts: `Tokens: XXX in, YYY out`
- Any retry/failure messages (indicators of 3B model reliability)

### Test 3: Verify Database

Check that `voice_insights.db` was created in the `backend/` directory.

Query the database (using SQLite CLI or Python):

```powershell
sqlite3 voice_insights.db "SELECT COUNT(*) FROM sessions; SELECT COUNT(*) FROM insights; SELECT COUNT(*) FROM llm_calls;"
```

Expected output (after running one analysis):
```
1
2
1
```

---

## Observability: Checking LLM Call Logs

Query the full LLM call details:

```powershell
sqlite3 voice_insights.db -header -column "SELECT session_id, latency_ms, retry_count, input_tokens, output_tokens, success FROM llm_calls;"
```

This shows latency and retry patterns — crucial for evaluating the 3B model's reliability.

---

## Troubleshooting

### Error: "Connection refused" (Ollama not running)

**Solution:** Start Ollama. On Windows, Ollama auto-starts as a service, but you can manually start it:
```powershell
ollama serve
```

### Error: "model not found"

**Solution:** Pull the model:
```powershell
ollama pull qwen2.5:3b-instruct
```

### Error: "JSON validation failed" in /analyze response

**Solution:** This indicates the 3B model's structured-output reliability issue. Check the terminal logs for the raw Ollama response. This is expected and will be tracked in Phase 4 (eval harness).

### Slow responses (>10s latency)

**Solution:** Local inference is slower than hosted APIs. This is intentional. Monitor `latency_ms` in the observability panel (Phase 3).

---

## Next Steps

1. **Verify Ollama is running** and model is pulled
2. **Start the backend server** with `uvicorn`
3. **Run the three tests** above
4. **Check terminal logs and database** for LLM call metadata
5. **Proceed to Phase 2** (Pipecat voice agent integration)

---

## Project Structure Reminder

- `main.py` — FastAPI app entry point
- `api/analysis.py` — POST /analyze endpoint
- `api/websocket.py` — WebSocket /ws/session/{session_id} endpoint
- `analysis/ollama_client.py` — Ollama client with retry logic + logging
- `analysis/schemas.py` — Pydantic models (Insight, AnalysisRequest, AnalysisResponse)
- `db/schema.py` — SQLite schema + data access functions
- `requirements.txt` — Python dependencies
