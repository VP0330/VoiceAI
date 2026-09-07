# Voice-to-Insight Frontend

React + Vite + Tailwind CSS frontend for the Voice-to-Insight platform.

## Project Structure

```
frontend/
├── src/
│   ├── components/          # React components
│   │   ├── SessionView.tsx    # Recording & transcript display
│   │   ├── InsightsPanel.tsx  # Insights theme cards
│   │   ├── MetricsPanel.tsx   # LLM performance metrics
│   │   └── SessionHistory.tsx # Past sessions list
│   ├── hooks/               # Custom React hooks
│   │   ├── useSession.ts      # Session state management
│   │   ├── useWebSocket.ts    # WebSocket connection
│   │   └── useVoiceRecorder.ts # Audio recording
│   ├── types/               # TypeScript interfaces
│   │   └── index.ts
│   ├── App.tsx              # Main app component
│   ├── main.tsx             # Entry point
│   └── index.css            # Global styles
├── index.html               # HTML entry point
├── package.json
├── tsconfig.json
├── vite.config.ts
├── tailwind.config.js
└── postcss.config.js
```

## Installation

```bash
cd frontend
npm install
```

## Development

Start the development server with hot reload:

```bash
npm run dev
```

The frontend will be available at `http://localhost:5173`

### Backend Proxy

Vite is configured to proxy API requests to the backend:
- `/api/*` → `http://localhost:8000`
- `/ws/*` → `ws://localhost:8000`

Make sure the backend is running on port 8000.

## Build

Create an optimized production build:

```bash
npm run build
```

Output is in `dist/`

## Preview

Preview the production build locally:

```bash
npm run preview
```

## Key Features

### SessionView Component
- 🎤 Start/stop voice recording
- 📝 Real-time transcript display (scrolls to bottom)
- ⏳ Loading indicator during processing
- ✅ WebSocket connection status
- ❌ Error display

### InsightsPanel Component
- 🎨 Grid layout of extracted insights
- 📊 Sentiment badges (positive/negative/neutral)
- 💬 Original quote display
- ✓ Actionability checkmark
- 💡 AI recommendations

### MetricsPanel Component
- ⏱️ Response latency (ms)
- 📥 Input token count
- 📤 Output token count
- 🔄 Total token count
- ↩️ Retry count
- 📈 Efficiency score (output/input ratio)
- 🐛 Raw debug info (JSON)

### Custom Hooks

#### useSession
- Manages session state (id, transcript turns, insights)
- Provides methods to add transcript turns and set insights
- Tracks loading state and errors

#### useWebSocket
- Connects to `/ws/session/{sessionId}` WebSocket
- Handles incoming messages (transcript broadcasts)
- Provides `sendTranscriptTurn()` to broadcast updates
- Auto-reconnect on disconnect

#### useVoiceRecorder
- MediaRecorder API for browser audio capture
- Records to WAV format
- Uploads to `/api/voice/process`
- Handles errors and permission prompts

## Backend API Integration

### Voice Processing Endpoint

**POST /api/voice/process**
```
Content-Type: multipart/form-data

session_id: string
audio_file: File (wav/mp3/ogg)

Response:
{
  "session_id": "...",
  "transcript": "...",
  "insights": [...],
  "llm_metadata": {...},
  "response_text": "...",
  "response_audio": "<base64>"
}
```

### WebSocket Streaming

**WS /ws/session/{sessionId}**
```
Incoming:
{ "type": "transcript_turn", "speaker": "user|agent", "text": "..." }

Outgoing:
{ "type": "transcript_turn_broadcast", "speaker": "...", "text": "..." }
```

## Styling

The frontend uses **Tailwind CSS** for styling with custom configuration:
- Responsive design (mobile, tablet, desktop)
- Color-coded insights (sentiment badges)
- Gradient backgrounds for metrics
- Smooth animations and transitions
- Custom scrollbar styling

## Browser Support

- Chrome/Chromium (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)

Requires support for:
- MediaRecorder API (audio recording)
- WebSocket API (real-time streaming)
- Fetch API (HTTP requests)
- Web Audio API (optional)

## Troubleshooting

### "Failed to start recording" error
- Check microphone permissions in browser settings
- Ensure HTTPS or localhost (some browsers require secure context)

### WebSocket connection fails
- Verify backend is running on port 8000
- Check browser console for errors
- Ensure proxy is configured correctly in vite.config.ts

### Styles not loading
- Run `npm install` to ensure Tailwind is installed
- Clear browser cache
- Rebuild: `npm run build`

## Future Enhancements

- [ ] Session history with database persistence
- [ ] Export insights as PDF/JSON
- [ ] Dark mode toggle
- [ ] Multi-language support
- [ ] Real-time collaboration
- [ ] Audio playback of agent responses
- [ ] Advanced filtering and search
- [ ] Analytics dashboard
