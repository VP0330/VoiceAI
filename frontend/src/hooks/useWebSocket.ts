import { useEffect, useRef, useState, useCallback } from 'react';
import { WebSocketMessage, TranscriptTurn } from '../types';

export const useWebSocket = (sessionId: string) => {
  const ws = useRef<WebSocket | null>(null);
  const [isConnected, setIsConnected] = useState(false);
  const [lastMessage, setLastMessage] = useState<WebSocketMessage | null>(null);

  const connect = useCallback(() => {
    if (ws.current) return;

    const protocol = window.location.protocol === 'https:' ? 'wss' : 'ws';
    const apiHost = import.meta.env.VITE_API_HOST || 'localhost:8000';
    const url = `${protocol}://${apiHost}/ws/session/${sessionId}`;

    ws.current = new WebSocket(url);

    ws.current.onopen = () => {
      console.log('[WebSocket] Connected');
      setIsConnected(true);
    };

    ws.current.onmessage = (event) => {
      try {
        const message = JSON.parse(event.data) as WebSocketMessage;
        console.log('[WebSocket] Message:', message);
        setLastMessage(message);
      } catch (err) {
        console.error('[WebSocket] Parse error:', err);
      }
    };

    ws.current.onerror = (error) => {
      console.error('[WebSocket] Error:', error);
    };

    ws.current.onclose = () => {
      console.log('[WebSocket] Disconnected');
      setIsConnected(false);
      ws.current = null;
    };
  }, [sessionId]);

  const disconnect = useCallback(() => {
    if (ws.current) {
      ws.current.close();
      ws.current = null;
      setIsConnected(false);
    }
  }, []);

  const sendTranscriptTurn = useCallback(
    (speaker: 'user' | 'agent', text: string, timestamp_ms: number = 0) => {
      if (!ws.current || ws.current.readyState !== WebSocket.OPEN) {
        console.warn('[WebSocket] Not connected');
        return;
      }

      const message: WebSocketMessage = {
        type: 'transcript_turn',
        speaker,
        text,
        timestamp_ms,
      };

      ws.current.send(JSON.stringify(message));
    },
    []
  );

  useEffect(() => {
    connect();
    return () => disconnect();
  }, [connect, disconnect, sessionId]);

  return {
    isConnected,
    lastMessage,
    sendTranscriptTurn,
    connect,
    disconnect,
  };
};
