import { useState, useCallback } from 'react';
import { Session, TranscriptTurn, Insight, LLMMetadata } from '../types';

export const useSession = (sessionId?: string) => {
  const [session, setSession] = useState<Session>({
    id: sessionId || `session-${Date.now()}`,
    created_at: new Date().toISOString(),
    transcript_turns: [],
    insights: [],
  });

  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const addTranscriptTurn = useCallback((turn: TranscriptTurn) => {
    setSession((prev) => ({
      ...prev,
      transcript_turns: [...prev.transcript_turns, turn],
    }));
  }, []);

  const setInsights = useCallback((insights: Insight[], metadata: LLMMetadata) => {
    setSession((prev) => ({
      ...prev,
      insights,
      llm_metadata: metadata,
    }));
  }, []);

  const clearSession = useCallback(() => {
    setSession({
      id: `session-${Date.now()}`,
      created_at: new Date().toISOString(),
      transcript_turns: [],
      insights: [],
    });
    setError(null);
  }, []);

  return {
    session,
    isLoading,
    setIsLoading,
    error,
    setError,
    addTranscriptTurn,
    setInsights,
    clearSession,
  };
};
