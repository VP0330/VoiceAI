import { useState } from 'react';
import { Insight, LLMMetadata } from '../types';

interface InsightsPanelProps {
  insights: Insight[];
  metadata?: LLMMetadata;
}

const sentimentColor = (sentiment: string) => {
  switch (sentiment) {
    case 'positive':
      return 'bg-green-100 text-green-800 border-green-300';
    case 'negative':
      return 'bg-red-100 text-red-800 border-red-300';
    case 'neutral':
      return 'bg-gray-200 text-gray-800 border-gray-300';
    default:
      return 'bg-gray-200 text-gray-800 border-gray-300';
  }
};

const sentimentEmoji = (sentiment: string) => {
  switch (sentiment) {
    case 'positive':
      return '😊';
    case 'negative':
      return '😞';
    case 'neutral':
      return '😐';
    default:
      return '😐';
  }
};

export const InsightsPanel = ({ insights, metadata }: InsightsPanelProps) => {
  const [showDebug, setShowDebug] = useState(false);

  if (insights.length === 0) {
    return (
      <div className="bg-gray-100 rounded-lg border border-gray-300 p-4 text-center">
        <p className="text-gray-500 text-sm">No insights yet</p>
      </div>
    );
  }

  return (
    <div className="space-y-3 flex flex-col h-full">
      {/* Sticky Header */}
      <div className="sticky top-0 bg-gray-50 border-b border-gray-200 pb-2 z-10">
        <h2 className="text-sm font-semibold text-gray-700 uppercase tracking-wider mb-4">✨ Insights</h2>
      </div>

      {/* Scrollable Insights Grid */}
      <div className="grid grid-cols-1 gap-3 overflow-y-auto flex-1">
        {insights.map((insight, idx) => (
          <div
            key={idx}
            className="bg-white rounded-lg border border-gray-200 p-4 hover:shadow-md transition-shadow"
          >
            {/* Theme Header */}
            <div className="flex items-start justify-between mb-2">
              <h3 className="font-semibold text-gray-900 flex-1 text-sm">{insight.theme}</h3>
              <span className={`px-2 py-1 rounded-full border text-xs font-medium ml-2 ${sentimentColor(insight.sentiment)}`}>
                {sentimentEmoji(insight.sentiment)} {insight.sentiment}
              </span>
            </div>

            {/* Quote */}
            <div className="mb-2 p-2 bg-gray-50 rounded border-l-4 border-blue-500">
              <p className="text-xs text-gray-700 italic">"{insight.quote}"</p>
            </div>

            {/* Actionability */}
            <div className="flex items-center gap-2 mb-2">
              <input
                type="checkbox"
                checked={insight.actionable}
                readOnly
                className="w-3 h-3 text-blue-600 rounded cursor-pointer"
              />
              <span className="text-xs font-medium text-gray-700">
                {insight.actionable ? '✓ Actionable' : 'Not actionable'}
              </span>
            </div>

            {/* Recommendation */}
            {insight.recommendation && (
              <div className="p-2 bg-blue-50 rounded border border-blue-200">
                <p className="text-xs text-gray-800">
                  <span className="font-semibold text-blue-900">💡</span> {insight.recommendation}
                </p>
              </div>
            )}
          </div>
        ))}
      </div>

            {/* Metadata Footer */}
      {metadata && (
        <div className="bg-gray-100 rounded-lg border border-gray-300 p-3 mt-auto">
          <button
            onClick={() => setShowDebug(!showDebug)}
            className="text-xs font-semibold text-gray-600 hover:text-gray-900 uppercase tracking-wide cursor-pointer hover:underline"
          >
            {showDebug ? '✕ Hide Debug' : '⚙️ Show Debug'}
          </button>

          {/* Metrics and Debug Info - Only show when debug is enabled */}
          {showDebug && (
            <>
              <div className="grid grid-cols-2 gap-2 text-xs mt-3">
                <div className="bg-white p-2 rounded">
                  <p className="text-gray-600">Latency</p>
                  <p className="text-gray-900 font-semibold">{metadata.latency_ms}ms</p>
                </div>
                <div className="bg-white p-2 rounded">
                  <p className="text-gray-600">Tokens</p>
                  <p className="text-gray-900 font-semibold">{metadata.total_tokens}</p>
                </div>
                <div className="bg-white p-2 rounded">
                  <p className="text-gray-600">Input</p>
                  <p className="text-gray-900 font-semibold">{metadata.input_tokens}</p>
                </div>
                <div className="bg-white p-2 rounded">
                  <p className="text-gray-600">Output</p>
                  <p className="text-gray-900 font-semibold">{metadata.output_tokens}</p>
                </div>
              </div>

              {/* Debug Info */}
              <div className="mt-2 p-2 bg-white rounded border border-gray-300">
                <pre className="text-xs text-gray-700 font-mono overflow-auto max-h-24">
                  {JSON.stringify(metadata, null, 2)}
                </pre>
              </div>
            </>
          )}
        </div>
      )}
      </div>
  );
};