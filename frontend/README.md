# 🎙️ VoiceAI Frontend

React + TypeScript + Vite frontend for the Voice Interview Analysis Platform.

## 📦 Technology Stack

- **React 18** - UI library
- **TypeScript** - Type safety
- **Vite** - Build tool and dev server
- **Tailwind CSS** - Styling
- **PostCSS** - CSS processing
- **Web Audio API** - Voice recording
- **WebSocket** - Real-time updates

## 📂 Project Structure

```
frontend/
├── src/
│   ├── components/
│   │   ├── index.ts                    # Component exports
│   │   ├── SessionView.tsx             # Recording & transcript display
│   │   ├── InsightsPanel.tsx           # Insights & sentiment badges
│   │   ├── MetricsPanel.tsx            # Performance metrics
│   │   └── SessionHistory.tsx          # Past sessions list
│   ├── hooks/
│   │   ├── index.ts                    # Hook exports
│   │   ├── useSession.ts               # Session state management
│   │   ├── useWebSocket.ts             # WebSocket integration
│   │   └── useVoiceRecorder.ts         # Audio recording
│   ├── types/
│   │   └── index.ts                    # TypeScript interfaces
│   ├── App.tsx                         # Main app component
│   ├── main.tsx                        # Entry point
│   └── index.css                       # Global styles
├── public/                             # Static assets
├── index.html                          # HTML entry point
├── package.json
├── vite.config.ts
├── tsconfig.json
├── tailwind.config.js
├── postcss.config.js
├── .env                                # Environment variables
└── README.md                           # This file
```

## 🚀 Quick Start

### Prerequisites

- Node.js 18+
- npm or yarn
- Backend running on `localhost:8000`

### Installation

```bash
cd frontend
npm install
```

### Development Server

```bash
npm run dev
```

Server starts at `http://localhost:5173` with hot module replacement (HMR).

### Build for Production

```bash
npm run build
```

Outputs optimized bundle to `dist/` folder.

### Preview Production Build

```bash
npm run preview
```

## 🌐 Environment Configuration

Create `frontend/.env`:

```env
# API Configuration
VITE_API_BASE_URL=
VITE_API_HOST=localhost:8000
```

**Notes:**
- `VITE_API_BASE_URL` - Leave empty to use relative paths (recommended for development)
- `VITE_API_HOST` - WebSocket server host:port

## 🎨 UI Layout

### Main Application

```
┌─────────────────────────────────────────────┐
│        VoiceInsights Header                 │
├──────────────┬──────────────────────────────┤
│              │                              │
│   Metrics    │    SessionView               │
│              │  ┌────────────────────────┐  │
│   Insights   │  │ Raw Transcript         │  │
│              │  ├────────────────────────┤  │
│              │  │ Analysis Summary (▼)   │  │
│              │  ├────────────────────────┤  │
│              │  │ Transcript Turns       │  │
│              │  │ User | Agent messages  │  │
│              │  ├────────────────────────┤  │
│              │  │ Controls:              │  │
│              │  │ 🎤 Record 📁 Upload   │  │
│              │  │ 🔄 New                │  │
│              │  └────────────────────────┘  │
└──────────────┴──────────────────────────────┘
```

### Sidebar (Left)
- **Header**: VoiceInsights branding + Session ID
- **Performance Metrics**: Response time, tokens, efficiency
- **Insights**: Extracted themes with sentiment badges

### Main Content (Right)
- **Raw Transcript**: Full audio text before parsing
- **Analysis Summary**: Collapsible key findings
- **Transcript**: User/agent conversation turns
- **Controls**: Record, upload, new session buttons

## 🔧 Components

### `App.tsx`
Main application component managing:
- Global state (session, loading, error)
- Component layout (sidebar + main content)
- Data flow between components

**Props passed to children:**
```tsx
<SessionView
  session={session}
  onAnalysisComplete={handleAnalysisComplete}
  isLoading={isLoading}
  setIsLoading={setIsLoading}
  onNewSession={handleNewSession}
  responseText={lastAnalysis?.response_text}
  rawTranscript={lastAnalysis?.transcript}
/>
```

### `SessionView.tsx`
Handles recording, uploading, and display of:
- Raw transcript (full audio text)
- Analysis summary (collapsible)
- Conversation transcript (user/agent turns)
- Loading/recording status
- Error messages

**Features:**
- Voice recording via Web Audio API
- File upload support
- Auto-scroll to latest message
- Real-time transcript streaming via WebSocket
- Performance metrics display

### `InsightsPanel.tsx`
Displays extracted insights in sidebar:
- Sticky header with consistent styling
- Individual insight cards with:
  - Theme title
  - Sentiment badge (color-coded)
  - Quote (italicized)
  - Actionable flag
  - Recommendation (if present)
- Debug toggle for metadata JSON

**Sentiment colors:**
- 🟢 Positive: bg-green-100, text-green-800
- 🔴 Negative: bg-red-100, text-red-800
- ⚫ Neutral: bg-gray-200, text-gray-800

### `MetricsPanel.tsx`
Shows LLM performance metrics:
- Response Time (blue)
- Input Tokens (green)
- Output Tokens (purple)
- Efficiency Ratio (orange)
- Debug toggle for full metadata JSON

**Features:**
- Compact 2x2 grid layout
- Color-coded status indicators
- Collapsible debug section

## 🪝 Custom Hooks

### `useSession.ts`
Session state management:
```tsx
const { 
  session,
  isLoading, 
  setIsLoading,
  error,
  setError,
  addTranscriptTurn,
  setInsights,
  clearSession 
} = useSession();
```

### `useVoiceRecorder.ts`
Audio recording via Web Audio API:
```tsx
const { 
  isRecording,
  error,
  startRecording,
  stopRecording,
  uploadAudio 
} = useVoiceRecorder();
```

**Supported formats:** WAV, MP3, OGG, FLAC

### `useWebSocket.ts`
Real-time transcript streaming:
```tsx
const { 
  isConnected,
  sendTranscriptTurn 
} = useWebSocket(sessionId);
```

**Connection:** Auto-connects to `ws://{VITE_API_HOST}/ws/session/{sessionId}`

## 📊 Type Definitions

Located in `types/index.ts`:

```typescript
interface Session {
  id: string;
  created_at: string;
  transcript_turns: TranscriptTurn[];
  insights: Insight[];
  llm_metadata?: LLMMetadata;
}

interface AnalysisResponse {
  session_id: string;
  transcript: string;           // Full audio transcript
  insights: Insight[];
  llm_metadata: LLMMetadata;
  response_text: string;        // Summary from LLM
  response_audio_base64?: string;
}

interface Insight {
  theme: string;
  quote: string;
  sentiment: 'positive' | 'neutral' | 'negative';
  actionable: boolean;
  recommendation?: string;
}

interface TranscriptTurn {
  speaker: 'user' | 'agent';
  text: string;
  timestamp_ms: number;
}

interface LLMMetadata {
  latency_ms: number;
  retry_count: number;
  input_tokens: number;
  output_tokens: number;
  total_tokens: number;
}
```

## 🎨 Styling

### Tailwind CSS Configuration
- **Color scheme**: White/light gray theme
- **Breakpoints**: Mobile-first responsive
- **Custom animations**: fadeIn, slideUp
- **Custom scrollbar**: Styled in `index.css`

### Global Styles (`index.css`)

```css
/* Scrollbar customization */
::-webkit-scrollbar { width: 8px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: #d1d5db; }

/* Animations */
@keyframes fadeIn { /* ... */ }
@keyframes slideUp { /* ... */ }

/* Utility classes */
.btn-primary, .btn-secondary, .card-modern
```

## 🔌 API Integration

### Recording & Upload Flow

```
1. User clicks "Record" → startRecording()
2. Audio recorded via Web Audio API (WAV format)
3. User clicks "Stop" → stopRecording()
4. Audio blob sent to backend: POST /api/voice/process
5. Backend returns: AnalysisResponse
6. Frontend displays: transcript, insights, metrics
```

### Real-time Streaming

```
1. SessionView connects to WebSocket: /ws/session/{session_id}
2. Backend sends transcript_turn messages in real-time
3. useWebSocket appends turns to session state
4. UI updates automatically
```

## 📱 Responsive Design

- **Desktop (>1024px)**: Full sidebar + main content
- **Tablet (768-1024px)**: Collapsible sidebar
- **Mobile (<768px)**: Stacked layout (sidebar below content)

## 🚦 Development Workflow

### Install Dependencies
```bash
npm install
```

### Start Dev Server
```bash
npm run dev
```

### Build for Production
```bash
npm run build
npm run preview  # Test production build locally
```

### Type Checking
```bash
npx tsc --noEmit
```

### Format Code (Optional)
```bash
npx prettier --write src/
```

## 🐛 Common Issues

### "Cannot GET /" when visiting localhost:5173

**Solution**: Ensure `npm run dev` is running and Vite dev server is active.

### "WebSocket connection refused"

**Solution**: Verify backend is running on `localhost:8000` and `.env` has correct `VITE_API_HOST`.

### "Failed to fetch audio from backend"

**Solution**: Check CORS is enabled in FastAPI backend:
```python
from fastapi.middleware.cors import CORSMiddleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Recording not working

**Solution**: Ensure browser has microphone permission and HTTPS is used in production (Web Audio API requires secure context).

## 📊 Performance Tips

1. **Lazy load components** - Use React.lazy() for large components
2. **Memoize expensive components** - Use React.memo() for insights panel
3. **Optimize re-renders** - Use useCallback for event handlers
4. **Bundle analysis** - Run `npm run build && npx vite-plugin-visualizer`

## 🔗 API Endpoints Used

- `POST /api/voice/process` - Process audio → transcript + analysis
- `WS /ws/session/{session_id}` - Real-time transcript streaming
- `POST /api/voice/session/start` - Create new session
- `GET /api/voice/sessions` - List sessions

## 📚 Resources

- [React Docs](https://react.dev)
- [TypeScript Docs](https://www.typescriptlang.org)
- [Vite Docs](https://vitejs.dev)
- [Tailwind CSS](https://tailwindcss.com)
- [Web Audio API](https://developer.mozilla.org/en-US/docs/Web/API/Web_Audio_API)
- [WebSocket API](https://developer.mozilla.org/en-US/docs/Web/API/WebSocket)

## 📝 License

MIT


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
