import { useState, useEffect } from 'react';
import { Session } from '../types';

interface SessionHistoryProps {
  currentSessionId: string;
  onSelectSession?: (sessionId: string) => void;
}

export const SessionHistory = ({ currentSessionId, onSelectSession }: SessionHistoryProps) => {
  const [sessions, setSessions] = useState<Session[]>([]);
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    const fetchSessions = async () => {
      try {
        setIsLoading(true);
        const apiBaseUrl = import.meta.env.VITE_API_BASE_URL || '';
        const response = await fetch(`${apiBaseUrl}/api/voice/sessions`);
        
        if (!response.ok) {
          console.error('Failed to fetch sessions:', response.statusText);
          return;
        }
        
        const data = await response.json();
        // Transform API response to Session format
        const transformedSessions = data.map((item: any) => ({
          id: item.session_id,
          created_at: item.created_at,
          insights: Array(item.insights_count).fill(null), // Placeholder for count
          transcript: item.transcript,
          status: item.status
        }));
        
        setSessions(transformedSessions);
      } catch (err) {
        console.error('Error fetching sessions:', err);
      } finally {
        setIsLoading(false);
      }
    };

    fetchSessions();
  }, []);

  if (sessions.length === 0) {
    return (
      <div className="bg-white rounded-lg border border-gray-200 p-6 text-center">
        <p className="text-gray-500">No previous sessions</p>
        <p className="text-sm text-gray-400 mt-2">Sessions will appear here as you create them</p>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg border border-gray-200 p-6">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">Session History</h3>

      <div className="space-y-2">
        {sessions.map((session) => (
          <div
            key={session.id}
            onClick={() => onSelectSession?.(session.id)}
            className={`p-3 rounded-lg border cursor-pointer transition-all ${
              currentSessionId === session.id
                ? 'bg-blue-50 border-blue-300 shadow-sm'
                : 'bg-gray-50 border-gray-200 hover:bg-gray-100'
            }`}
          >
            <div className="flex items-center justify-between">
              <div>
                <p className="font-medium text-gray-900">{session.id}</p>
                <p className="text-xs text-gray-500">
                  {new Date(session.created_at).toLocaleString()}
                </p>
              </div>
              <div className="text-right">
                <p className="text-sm font-semibold text-blue-600">{session.insights.length} insights</p>
                <p className="text-xs text-gray-500">{session.transcript_turns.length} turns</p>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
