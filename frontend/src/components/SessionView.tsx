import { useEffect, useRef, useState } from 'react';
import { useVoiceRecorder, useWebSocket } from '../hooks';
import { Session, AnalysisResponse } from '../types';

interface SessionViewProps {
  session: Session;
  onAnalysisComplete: (data: AnalysisResponse) => void;
  isLoading: boolean;
  setIsLoading: (loading: boolean) => void;
  onNewSession: () => void;
  responseText?: string;
  rawTranscript?: string;
}

export const SessionView = ({
  session,
  onAnalysisComplete,
  isLoading,
  setIsLoading,
  onNewSession,
  responseText,
  rawTranscript,
}: SessionViewProps) => {
  const { isRecording, error, startRecording, stopRecording, uploadAudio } = useVoiceRecorder();
  const { isConnected, sendTranscriptTurn } = useWebSocket(session.id);
  const transcriptEndRef = useRef<HTMLDivElement>(null);
  const [isAnalysisCollapsed, setIsAnalysisCollapsed] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    transcriptEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [session.transcript_turns]);

  const handleRecordingToggle = async () => {
    if (isRecording) {
      setIsLoading(true);
      try {
        const audioBlob = await stopRecording();
        if (audioBlob) {
          const result = await uploadAudio(session.id, audioBlob);
          console.log('[SessionView] Upload result:', result);
          
          if (result.transcript) {
            console.log('[SessionView] Adding user transcript');
            sendTranscriptTurn('user', result.transcript, Date.now());
          }
          
          console.log('[SessionView] Calling onAnalysisComplete');
          onAnalysisComplete(result);
          
          if (result.response_text) {
            sendTranscriptTurn('agent', result.response_text, Date.now());
          }
        }
      } catch (err) {
        console.error('Recording error:', err);
      } finally {
        setIsLoading(false);
      }
    } else {
      await startRecording();
    }
  };

  const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    setIsLoading(true);
    try {
      const result = await uploadAudio(session.id, file);
      console.log('[SessionView] File upload result:', result);
      
      if (result.transcript) {
        console.log('[SessionView] Adding user transcript from file');
        sendTranscriptTurn('user', result.transcript, Date.now());
      }
      
      console.log('[SessionView] Calling onAnalysisComplete');
      onAnalysisComplete(result);
      
      if (result.response_text) {
        sendTranscriptTurn('agent', result.response_text, Date.now());
      }
    } catch (err) {
      console.error('Upload error:', err);
    } finally {
      setIsLoading(false);
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
    }
  };

    return (
    <div className="flex flex-col h-full bg-white">
      {/* Transcript Box */}
      <div className="flex-1 overflow-y-auto p-6 space-y-4">
        {/* Raw Transcript Section */}
        {rawTranscript && (
          <div className="bg-gray-50 rounded-lg border border-gray-200 p-6">
            <h2 className="text-lg font-bold text-gray-900 mb-4">🎙️ Raw Transcript</h2>
            <div className="bg-white rounded p-4 border border-gray-300">
              <p className="text-gray-800 text-sm leading-relaxed">{rawTranscript}</p>
            </div>
          </div>
        )}

        {/* Analysis Summary - Moved Above Transcript */}
        {session.insights.length > 0 && (
          <div className="bg-blue-50 rounded-lg border border-blue-200 p-5">
            <div className="flex items-center justify-between mb-3">
              <h3 className="font-bold text-lg text-blue-900">📊 Analysis Summary</h3>
              <button
                onClick={() => setIsAnalysisCollapsed(!isAnalysisCollapsed)}
                className="text-blue-600 hover:text-blue-900 font-bold text-xl transition-colors"
                title={isAnalysisCollapsed ? 'Expand' : 'Collapse'}
              >
                {isAnalysisCollapsed ? '▶' : '▼'}
              </button>
            </div>
            {!isAnalysisCollapsed && (
              <>
                {session.llm_metadata && (
                  <div className="text-xs text-blue-800 mb-3 space-y-1 font-mono">
                    <p>⚡ <span className="font-semibold">Latency:</span> {session.llm_metadata.latency_ms}ms</p>
                    <p>📝 <span className="font-semibold">Tokens:</span> {session.llm_metadata.input_tokens} in, {session.llm_metadata.output_tokens} out</p>
                  </div>
                )}
                <p className="text-gray-800 text-sm leading-relaxed">
                  <span className="font-semibold text-blue-900">Key Findings:</span> {responseText || 'Processing...'}
                </p>
              </>
            )}
          </div>
        )}

        {/* Conversation Transcript Box */}
        <div className="bg-gray-50 rounded-lg border border-gray-200 p-6">
          <h2 className="text-lg font-bold text-gray-900 mb-4">📝 Transcript</h2>
          
          {session.transcript_turns.length === 0 ? (
            <div className="text-center py-8">
              <p className="text-gray-500 mb-2 text-sm">🎯 No transcript yet</p>
              <p className="text-xs text-gray-400">Click the record button or upload an audio file to get started</p>
            </div>
          ) : (
            <div className="space-y-3">
              {session.transcript_turns.map((turn, idx) => (
                <div
                  key={idx}
                  className={`p-3 rounded-lg border ${
                    turn.speaker === 'user'
                      ? 'bg-blue-50 border-l-4 border-blue-500'
                      : 'bg-purple-50 border-l-4 border-purple-500'
                  }`}
                >
                  <div className="flex items-center gap-2 mb-1">
                    <span className={`font-semibold text-xs ${turn.speaker === 'user' ? 'text-blue-900' : 'text-purple-900'}`}>
                      {turn.speaker === 'user' ? '👤 You' : '🤖 Agent'}
                    </span>
                    <span className="text-xs text-gray-500">
                      {new Date(turn.timestamp_ms).toLocaleTimeString()}
                    </span>
                  </div>
                  <p className="text-gray-800 text-sm">{turn.text}</p>
                </div>
              ))}
            </div>
          )}

          {isRecording && (
            <div className="p-3 bg-red-100 rounded-lg border border-red-300 animate-pulse mt-3">
              <p className="text-red-700 font-semibold text-sm">🔴 Recording...</p>
            </div>
          )}

          {isLoading && (
            <div className="p-3 bg-yellow-100 rounded-lg border border-yellow-300 mt-3">
              <p className="text-yellow-700 font-semibold text-sm">⏳ Processing...</p>
            </div>
          )}

          <div ref={transcriptEndRef} />
        </div>
      </div>

      {/* Error Display */}
      {error && (
        <div className="bg-red-100 border-t border-red-300 p-4">
          <p className="text-red-700 text-sm">
            <strong>⚠️ Error:</strong> {error}
          </p>
        </div>
      )}

      {/* Controls */}
      <div className="bg-white border-t border-gray-200 p-4 shadow-sm">
        <div className="flex items-center justify-between gap-4">
          <div className="text-sm">
            {isConnected ? (
              <span className="flex items-center gap-2 text-green-600">
                <span className="w-2 h-2 bg-green-600 rounded-full animate-pulse"></span>
                Connected
              </span>
            ) : (
              <span className="flex items-center gap-2 text-gray-500">
                <span className="w-2 h-2 bg-gray-500 rounded-full"></span>
                Connecting...
              </span>
            )}
          </div>

          <div className="flex gap-3">
            {/* Upload Audio Button */}
            <div>
              <input
                ref={fileInputRef}
                type="file"
                accept="audio/*"
                onChange={handleFileUpload}
                className="hidden"
                disabled={isLoading || isRecording}
              />
              <button
                onClick={() => fileInputRef.current?.click()}
                disabled={isLoading || isRecording}
                className={`px-4 py-2 rounded-lg font-semibold text-sm transition-all ${
                  isLoading || isRecording
                    ? 'bg-gray-300 text-gray-600 cursor-not-allowed'
                    : 'bg-purple-600 hover:bg-purple-700 text-white shadow-md'
                }`}
              >
                📁 Upload
              </button>
            </div>

            {/* Start Recording Button */}
            <button
              onClick={handleRecordingToggle}
              disabled={isLoading}
              className={`px-6 py-2 rounded-lg font-semibold text-sm transition-all ${
                isRecording
                  ? 'bg-red-600 hover:bg-red-700 text-white shadow-md'
                  : isLoading
                  ? 'bg-gray-300 text-gray-600 cursor-not-allowed'
                  : 'bg-blue-600 hover:bg-blue-700 text-white shadow-md'
              }`}
            >
              {isRecording ? '⏹️ Stop' : isLoading ? '⏳ Processing' : '🎤 Record'}
            </button>

            {/* New Session Button */}
            <button
              onClick={onNewSession}
              disabled={isLoading || isRecording}
              className={`px-4 py-2 rounded-lg font-semibold text-sm transition-all ${
                isLoading || isRecording
                  ? 'bg-gray-300 text-gray-600 cursor-not-allowed'
                  : 'bg-gray-600 hover:bg-gray-700 text-white shadow-md'
              }`}
            >
              🔄 New
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};