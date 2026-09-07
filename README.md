# 🎙️ VoiceAI

A real-time voice interview analysis system that captures audio, transcribes it, and generates AI-powered insights using FastAPI backend and React frontend.

## 📋 Features

- **Real-time Voice Recording** - Record audio directly in the browser or upload audio files
- **Automatic Transcription** - Deepgram Speech-to-Text integration
- **AI-Powered Analysis** - Ollama LLM generates structured insights with sentiment analysis
- **Live Transcript Streaming** - WebSocket integration for real-time updates
- **Performance Metrics** - Track latency, token usage, and efficiency
- **Session Persistence** - PostgreSQL database stores all data durably
- **Modern UI** - Clean white theme with left sidebar layout

## 🏗️ Architecture

### Frontend (React + TypeScript + Vite)
- **Components**: SessionView, InsightsPanel, MetricsPanel
- **Hooks**: useSession, useVoiceRecorder, useWebSocket
- **Styling**: Tailwind CSS with custom animations
- **State**: React hooks for session management

### Backend (FastAPI + Python)
- **LLM**: Ollama (qwen2.5:3b-instruct model)
- **STT**: Deepgram API
- **Database**: PostgreSQL 16
- **WebSocket**: Real-time transcript streaming
- **APIs**: RESTful endpoints for voice processing

## 📦 Tech Stack

- **Frontend**: React 18, TypeScript, Vite, Tailwind CSS
- **Backend**: FastAPI, Python 3.13, uvicorn
- **Database**: PostgreSQL 16 (Docker)
- **LLM**: Ollama (local inference)
- **Speech**: Deepgram (STT), pyttsx3 (TTS)
- **Real-time**: WebSocket

## 🚀 Quick Start

### Prerequisites
- Node.js 18+
- Python 3.13+
- PostgreSQL 16 (Docker recommended)
- Ollama 0.1.0+ (with qwen2.5:3b-instruct model)
- Deepgram API key

### 1. Backend Setup

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # macOS/Linux

pip install -r requirements.txt
```

Create `backend/.env`:
```env
OLLAMA_BASE_URL=http://localhost:11434/v1
OLLAMA_MODEL=qwen2.5:3b-instruct
DB_HOST=localhost
DB_PORT=5432
DB_NAME=voice_insights
DB_USER=voice_user
DB_PASSWORD=voice_password
API_HOST=0.0.0.0
API_PORT=8000
DEEPGRAM_API_KEY=your_key_here
```

Start PostgreSQL:
```bash
docker-compose up -d
```

Start Ollama:
```bash
ollama serve
ollama pull qwen2.5:3b-instruct
```

Run backend:
```bash
python main.py
```

### 2. Frontend Setup

```bash
cd frontend
npm install
```

Create `frontend/.env`:
```env
VITE_API_BASE_URL=
VITE_API_HOST=localhost:8000
```

Run frontend:
```bash
npm run dev
```

## 📂 Project Structure

```
Arbor/
├── backend/              # FastAPI backend
│   ├── main.py
│   ├── requirements.txt
│   ├── .env
│   ├── README.md
│   ├── analysis/         # LLM analysis module
│   ├── api/              # API routes
│   ├── db/               # Database schemas
│   └── voice/            # Voice processing
├── frontend/             # React frontend
│   ├── src/
│   ├── package.json
│   ├── vite.config.ts
│   ├── .env
│   └── README.md
├── docker-compose.yml    # PostgreSQL setup
├── .env.example          # Example env variables
└── README.md             # This file
```

## 🔌 API Endpoints

### Voice Processing
- `POST /api/voice/process` - Process audio and return transcript + analysis
- `POST /api/voice/session/start` - Create new session
- `GET /api/voice/session/{session_id}/status` - Get session status
- `GET /api/voice/sessions` - List all sessions
- `POST /api/voice/session/{session_id}/generate-audio` - Generate TTS audio
- `GET /api/voice/session/{session_id}/audio` - Retrieve generated audio

### WebSocket
- `WS /ws/session/{session_id}` - Real-time transcript streaming

## 📊 Data Flow

1. **Record/Upload** → User records audio or uploads file
2. **Transcribe** → Deepgram STT generates transcript
3. **Analyze** → Ollama LLM processes transcript
4. **Store** → PostgreSQL saves session data
5. **Display** → React updates UI with transcript, insights, metrics

## 🎯 UI Components

### SessionView
- Raw transcript display (full audio text)
- Conversation transcript (user/agent turns)
- Analysis summary with collapsible metrics
- Record/Upload/New Session controls

### InsightsPanel (Left Sidebar)
- Extracted insights with sentiment badges
- Actionable recommendations
- Sticky header with consistent styling

### MetricsPanel (Left Sidebar)
- Response time
- Token usage (input/output)
- Efficiency ratio
- Debug mode toggle

## 🔧 Configuration

### Environment Variables

**Backend (.env)**
- `OLLAMA_BASE_URL` - Ollama API endpoint
- `OLLAMA_MODEL` - Model name
- `DB_*` - Database credentials
- `DEEPGRAM_API_KEY` - Speech-to-text API key

**Frontend (.env)**
- `VITE_API_BASE_URL` - API base URL (leave empty for relative paths)
- `VITE_API_HOST` - WebSocket host:port

## 📈 Performance

- **Latency**: 15-20 seconds (record → transcribe → analyze → display)
- **Token Usage**: ~1000-2000 tokens per analysis
- **Database**: Connection pooling (1-20 connections)
- **LLM Retries**: 3 retries with exponential backoff

## 🐛 Troubleshooting

### Ollama Connection Error
```
HTTPConnectionPool(host='localhost', port=11434)
```
**Solution**: Ensure Ollama is running (`ollama serve`) and model is pulled (`ollama pull qwen2.5:3b-instruct`)

### Database Connection Error
```
FATAL: password authentication failed
```
**Solution**: Verify PostgreSQL is running (`docker-compose up`) and `.env` credentials match

### Deepgram API Error
```
401 Unauthorized
```
**Solution**: Verify `DEEPGRAM_API_KEY` is set correctly in `.env`

## 🚦 Health Check

```bash
curl http://localhost:8000/health
```

## 📚 Documentation

- [Backend README](backend/README.md) - Backend architecture and setup
- [Frontend README](frontend/README.md) - Frontend architecture and setup

## 📝 License

MIT

## 👨‍💻 Development

To run in development mode:
- Backend: `python main.py` (auto-reloads)
- Frontend: `npm run dev` (Vite dev server with HMR)

## 🔗 Resources

- [Ollama Documentation](https://ollama.ai)
- [Deepgram Docs](https://developers.deepgram.com)
- [FastAPI Docs](http://localhost:8000/docs) (when backend is running)
- [React Documentation](https://react.dev)
