import { useState } from 'react';
import { SessionView, InsightsPanel, MetricsPanel } from './components';
import { useSession } from './hooks';
import { AnalysisResponse } from './types';

function App() {
  const { session, isLoading, setIsLoading, error, setError, addTranscriptTurn, setInsights, clearSession } = useSession();
  const [lastAnalysis, setLastAnalysis] = useState<AnalysisResponse | null>(null);

  const handleAnalysisComplete = (data: AnalysisResponse) => {
    console.log('[App] Analysis complete:', data);
    setLastAnalysis(data);
    if (data.insights && data.llm_metadata) {
      console.log('[App] Setting insights:', data.insights.length, 'insights');
      setInsights(data.insights, data.llm_metadata);
    }
  };

  const handleNewSession = () => {
    clearSession();
    setLastAnalysis(null);
  };

  return (
    <div className="flex h-screen bg-gray-50">
      {/* Left Sidebar - Header, Metrics & Insights */}
      <div className="w-96 bg-white border-r border-gray-200 flex flex-col shadow-sm">
        {/* Header */}
        <div className="p-6 bg-white border-b border-gray-200">
          <h1 className="text-3xl font-bold text-gray-900">VoiceInsights</h1>
          <p className="text-xs text-gray-600 mt-2">
            Session: {session.id}
          </p>
        </div>

        {/* Metrics Section */}
        <div className="flex-1 p-6 border-b border-gray-200 overflow-y-auto">
          <h2 className="text-sm font-semibold text-gray-700 uppercase tracking-wider mb-4">🚨 Performance Metrics</h2>
          <MetricsPanel metadata={lastAnalysis?.llm_metadata} isLoading={isLoading} />
        </div>

        {/* Insights Section */}
        <div className="flex-1 p-6 bg-gray-50 overflow-y-auto">
          <InsightsPanel insights={session.insights} metadata={lastAnalysis?.llm_metadata} />
        </div>
      </div>

      {/* Main Content - Recording Area */}
      <div className="flex-1 flex flex-col overflow-hidden">
        <SessionView
          session={session}
          onAnalysisComplete={handleAnalysisComplete}
          isLoading={isLoading}
          setIsLoading={setIsLoading}
          onNewSession={handleNewSession}
          responseText={lastAnalysis?.response_text}
          rawTranscript={lastAnalysis?.transcript}
        />
      </div>
    </div>
  );
}

export default App;
