# 🎙️VoiceAI Analysis Platform

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
