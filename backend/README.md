# Voice-to-Insight Backend — Phase 1 & Phase 2 Setup

## Architecture Overview

**Phase 1 (✅ Complete):** REST API for structured analysis
- ✅ `/api/analyze` — Submit transcript → get structured insights
- ✅ PostgreSQL database with connection pooling
- ✅ Ollama LLM integration with retry logic

**Phase 2 (🔄 In Development):** Full voice loop with real-time streaming
- 🔄 `/api/voice/process` — Voice input → transcript → analysis → voice response
- 🔄 WebSocket `/ws/session/{session_id}` — Real-time transcript streaming
- 🔄 Deepgram STT (speech-to-text)
- 🔄 ElevenLabs TTS (text-to-speech)
- 🔄 Pipecat voice agent framework

---

## Prerequisites

1. **Python 3.13** installed
2. **Docker** installed (for PostgreSQL container)
3. **Ollama** installed with `qwen2.5:3b-instruct` model
4. **API Keys (for Phase 2):**
   - Deepgram API key (free tier: https://deepgram.com)
   - ElevenLabs API key (free tier: https://elevenlabs.io)

---

## Phase 1: Setup & Installation

### Step 1: Install Ollama

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

### Step 3: Start PostgreSQL Container

From the **root project directory** (not backend/):

```powershell
docker-compose up -d
```

Verify PostgreSQL is running:
```powershell
docker ps | findstr voice-to-insight-db
```

You should see: `voice-to-insight-db`

To view logs:
```powershell
docker-compose logs postgres
```

To stop PostgreSQL:
```powershell
docker-compose down
```

### Step 4: Verify Ollama Endpoint

Test the OpenAI-compatible endpoint:

```powershell
curl http://localhost:11434/v1/models
```

You should see a JSON response listing `qwen2.5:3b-instruct`.

### Step 5: Install Python Dependencies

From the `backend/` directory:

```powershell
pip install -r requirements.txt
```

### Step 6: Verify `.env` Configuration

The `.env` file should already be configured to match `docker-compose.yml`:

```
DB_HOST=localhost
DB_PORT=5432
DB_NAME=voice_insights
DB_USER=voice_user
DB_PASSWORD=voice_password
OLLAMA_BASE_URL=http://localhost:11434/v1
OLLAMA_MODEL=qwen2.5:3b-instruct
```

Customize if your PostgreSQL is on a different host.

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
[INFO] main: Connection pool initialized
[INFO] main: Database schema ready
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

```powershell
$body = @{
    transcript = "Interviewer: Tell me about your biggest challenge at work. Interviewee: Time management is tough. I have five projects running in parallel, and it's hard to prioritize. I found that blocking time on calendar helps a lot."
    session_id = "test-session-001"
} | ConvertTo-Json

Invoke-WebRequest -Uri http://localhost:8000/api/analyze `
  -Method Post `
  -Body $body `
  -ContentType "application/json" `
  -UseBasicParsing | Select-Object -ExpandProperty Content
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

### Test 3: Query PostgreSQL Database

Connect to PostgreSQL using any client:

```powershell
# Using psql if installed
psql -h localhost -U voice_user -d voice_insights -c "SELECT * FROM sessions;"

# Or query from Python
python -c "
import psycopg2
conn = psycopg2.connect('host=localhost user=voice_user password=voice_password dbname=voice_insights')
cursor = conn.cursor()
cursor.execute('SELECT COUNT(*) FROM sessions;')
print(f'Total sessions: {cursor.fetchone()[0]}')
conn.close()
"
```

### Test 4: View Data in DBeaver (Optional, Recommended)

1. Download **DBeaver Community** from https://dbeaver.io
2. Install and open
3. Create new PostgreSQL connection:
   - **Host**: localhost
   - **Port**: 5432
   - **Database**: voice_insights
   - **User**: voice_user
   - **Password**: voice_password
4. Connect and browse `sessions`, `insights`, `llm_calls` tables in real-time

This is **much easier** than CLI queries and great for demonstrations!

---

## Troubleshooting

### Error: "connection refused" (PostgreSQL not running)

**Solution:** Start PostgreSQL container:
```powershell
docker-compose up -d
docker-compose logs postgres  # Check for startup errors
```

### Error: "psycopg2.OperationalError: authentication failed"

**Solution:** Verify credentials in `.env` match `docker-compose.yml`:
```
DB_USER=voice_user
DB_PASSWORD=voice_password
```

### Error: "relation 'sessions' does not exist"

**Solution:** Delete the container and reinitialize:
```powershell
docker-compose down -v  # -v removes volume (all data)
docker-compose up -d
# Restart FastAPI backend — schema will be auto-created
```

### Error: "Ollama connection refused"

**Solution:** Start Ollama:
```powershell
ollama serve
```

### Slow Responses (>10s latency)

**Solution:** Local inference is slower than hosted APIs. This is intentional. Monitor `latency_ms` in the observability panel (Phase 3).

---

## Database Management

### View All Sessions

```sql
SELECT id, created_at FROM sessions ORDER BY created_at DESC;
```

### View Insights from a Session

```sql
SELECT session_id, theme, sentiment, actionable, recommendation FROM insights WHERE session_id = 'test-session-001';
```

### View LLM Call Metrics

```sql
SELECT 
  session_id, 
  latency_ms, 
  retry_count, 
  input_tokens, 
  output_tokens, 
  success 
FROM llm_calls 
WHERE success = true
ORDER BY created_at DESC;
```

### Database Stats

```sql
SELECT 
  COUNT(DISTINCT session_id) as total_sessions,
  COUNT(*) as total_insights,
  AVG(latency_ms) as avg_latency_ms,
  MAX(latency_ms) as max_latency_ms
FROM insights i
JOIN llm_calls c ON i.session_id = c.session_id;
```

---

## Phase 2: Voice Agent (In Development)

### Architecture

```
User Voice Input
    ↓
[Deepgram STT] → Transcript
    ↓
[WebSocket] → Real-time stream
    ↓
[Ollama LLM] → Extract insights
    ↓
[Response Generator] → Conversational text
    ↓
[ElevenLabs TTS] → Audio response
    ↓
User Hears Response
```

### Phase 2 Code Structure

```
backend/
├── voice/
│   ├── __init__.py
│   ├── pipecat_agent.py       # Main voice agent with full loop
│   ├── deepgram_client.py     # Deepgram STT integration
│   └── elevenlabs_client.py   # ElevenLabs TTS integration
├── api/
│   ├── voice.py               # Voice endpoints (NEW)
│   ├── analysis.py            # Phase 1 analysis
│   └── websocket.py           # WebSocket with voice streaming
└── main.py                    # Updated with voice router
```

### New Dependencies (Added to requirements.txt)

```
pipecat-ai==0.0.42             # Voice agent framework
deepgram-sdk==3.4.0            # Speech-to-text
elevenlabs==0.2.28             # Text-to-speech
aiohttp==3.10.0                # Async HTTP
```

### Phase 2: Configure API Keys

Update `backend/.env`:

```env
# Deepgram (get key from https://console.deepgram.com)
DEEPGRAM_API_KEY=your_deepgram_key_here

# pyttsx3 (local TTS, no API key needed)
# Optional: TTS_VOICE_ID=default (uses system default voice)
```

### Phase 2: New Endpoints

#### 1. Start Voice Session

**Request:**
```
POST /api/voice/session/start
Content-Type: application/json

{
  "session_id": "optional-custom-id"
}
```

**Response:**
```json
{
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "websocket_url": "ws://localhost:8000/ws/session/550e8400-e29b-41d4-a716-446655440000",
  "status": "ready"
}
```

#### 2. Process Voice Input

**Request:**
```
POST /api/voice/process
Content-Type: multipart/form-data

session_id: 550e8400-e29b-41d4-a716-446655440000
audio_file: <.wav/.mp3/.ogg file>
```

**Response:**
```json
{
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "transcript": "Tell me about your biggest achievement",
  "insights": [
    {
      "theme": "Team Leadership",
      "quote": "I led a team that improved efficiency",
      "sentiment": "positive",
      "actionable": true,
      "recommendation": "Document and replicate this process"
    }
  ],
  "llm_metadata": {
    "latency_ms": 3500,
    "retry_count": 0,
    "input_tokens": 145,
    "output_tokens": 62,
    "total_tokens": 207
  },
  "response_text": "Great story about team leadership!",
  "response_audio": "<base64-encoded mp3>"
}
```

#### 3. WebSocket Real-time Stream

**URL:** `ws://localhost:8000/ws/session/{session_id}`

**Incoming Messages (from client):**
```json
{
  "type": "transcript_turn",
  "speaker": "user",
  "text": "Hello, can you hear me?",
  "timestamp_ms": 1234
}
```

**Outgoing Messages (from server):**
```json
{
  "type": "transcript_turn_broadcast",
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "speaker": "agent",
  "text": "Yes, I can hear you!",
  "timestamp_ms": 5678
}
```

### Phase 2: Testing (Manual)

#### Test 1: Create Voice Session

```powershell
Invoke-WebRequest -Uri http://localhost:8000/api/voice/session/start `
  -Method Post `
  -ContentType "application/json" `
  -Body (@{} | ConvertTo-Json) `
  -UseBasicParsing | Select-Object -ExpandProperty Content
```

#### Test 2: Send Audio File

```powershell
$file = Get-Item "path/to/audio.wav"
$session_id = "test-voice-001"

$form = @{
    session_id = $session_id
}

# Use form data to upload file
Invoke-WebRequest -Uri http://localhost:8000/api/voice/process `
  -Method Post `
  -Form $form `
  -File @{audio_file = $file} `
  -UseBasicParsing
```

#### Test 3: WebSocket Streaming

Use any WebSocket client (e.g., wscat, or frontend):

```
wscat -c ws://localhost:8000/ws/session/test-voice-001

# Send:
{"type": "transcript_turn", "speaker": "user", "text": "Tell me a story"}

# Receive:
{"type": "transcript_turn_broadcast", "speaker": "agent", "text": "..."}
```

---

## Next Steps

1. ✅ **Phase 1:** REST API + PostgreSQL (DONE)
2. 🔄 **Phase 2:** Pipecat voice agent with Deepgram + ElevenLabs (IN PROGRESS)
3. ⏭️ **Phase 3:** React + Vite frontend with live session view
4. ⏭️ **Phase 4:** Evaluation harness for model reliability

---

## Resources

- **Ollama:** https://ollama.com
- **Deepgram:** https://console.deepgram.com
- **ElevenLabs:** https://elevenlabs.io/app/api-keys
- **Pipecat:** https://github.com/pipecat-ai/pipecat
- **FastAPI:** https://fastapi.tiangolo.com
- **PostgreSQL:** https://www.postgresql.org

---

## Next Steps

1. **Verify Ollama is running** with model pulled
2. **Start PostgreSQL** with Docker: `docker-compose up -d`
3. **Install Python dependencies**: `pip install -r requirements.txt`
4. **Start backend server**: `python -m uvicorn main:app --reload`
5. **Run tests** (see Testing section above)
6. **Proceed to Phase 2** (Pipecat voice agent integration)

---

## Project Structure Reminder

- `main.py` — FastAPI app entry point
- `api/analysis.py` — POST /analyze endpoint
- `api/websocket.py` — WebSocket /ws/session/{session_id} endpoint
- `analysis/ollama_client.py` — Ollama client with retry logic + logging
- `analysis/schemas.py` — Pydantic models (Insight, AnalysisRequest, AnalysisResponse)
- `db/schema.py` — PostgreSQL schema + connection pooling
- `requirements.txt` — Python dependencies
- `../.env` — Environment configuration (PostgreSQL credentials, Ollama endpoint)
- `../docker-compose.yml` — PostgreSQL container setup
