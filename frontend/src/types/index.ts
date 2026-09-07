export interface Insight {
  theme: string;
  quote: string;
  sentiment: 'positive' | 'neutral' | 'negative';
  actionable: boolean;
  recommendation?: string;
}

export interface LLMMetadata {
  latency_ms: number;
  retry_count: number;
  input_tokens: number;
  output_tokens: number;
  total_tokens: number;
}

export interface AnalysisResponse {
  session_id: string;
  transcript: string;
  insights: Insight[];
  llm_metadata: LLMMetadata;
  response_text: string;
  response_audio_base64?: string | null;
}

export interface TranscriptTurn {
  speaker: 'user' | 'agent';
  text: string;
  timestamp_ms: number;
}

export interface Session {
  id: string;
  created_at: string;
  transcript_turns: TranscriptTurn[];
  insights: Insight[];
  llm_metadata?: LLMMetadata;
}

export interface WebSocketMessage {
  type: 'transcript_turn' | 'transcript_turn_received' | 'transcript_turn_broadcast' | 'audio_chunk_ack' | 'control_ack';
  session_id?: string;
  speaker?: 'user' | 'agent';
  text?: string;
  timestamp_ms?: number;
  action?: string;
  status?: string;
}
