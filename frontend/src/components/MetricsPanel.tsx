import { useState } from 'react';
import { LLMMetadata } from '../types';

interface MetricsPanelProps {
  metadata?: LLMMetadata;
  isLoading?: boolean;
}

export const MetricsPanel = ({ metadata, isLoading }: MetricsPanelProps) => {
  const [showDebug, setShowDebug] = useState(false);

  if (!metadata && !isLoading) {
    return (
      <div className="bg-gray-100 rounded-lg border border-gray-300 p-4 text-center">
        <p className="text-gray-500 text-sm">No metrics available</p>
      </div>
    );
  }

  return (
    <div>
      {isLoading ? (
        <div className="text-center py-6">
          <div className="animate-spin inline-block w-6 h-6 border-3 border-gray-300 border-t-blue-600 rounded-full"></div>
          <p className="text-gray-600 mt-2 text-sm">Processing...</p>
        </div>
      ) : metadata ? (
        <div className="grid grid-cols-2 gap-2">
          {/* Latency */}
          <div className="bg-blue-50 rounded-lg p-3 border border-blue-200 hover:border-blue-300 transition-colors">
            <p className="text-xs font-semibold text-blue-700 uppercase tracking-wide">Response Time</p>
            <p className="text-xl font-bold text-blue-900 mt-1">{metadata.latency_ms}ms</p>
            <p className="text-xs text-blue-600 mt-1">
              {metadata.latency_ms < 2000 ? '⚡ Fast' : metadata.latency_ms < 5000 ? '✓ Normal' : '⏳ Slow'}
            </p>
          </div>

          {/* Input Tokens */}
          <div className="bg-green-50 rounded-lg p-3 border border-green-200 hover:border-green-300 transition-colors">
            <p className="text-xs font-semibold text-green-700 uppercase tracking-wide">Input</p>
            <p className="text-xl font-bold text-green-900 mt-1">{metadata.input_tokens}</p>
            <p className="text-xs text-green-600 mt-1">Tokens</p>
          </div>

          {/* Output Tokens */}
          <div className="bg-purple-50 rounded-lg p-3 border border-purple-200 hover:border-purple-300 transition-colors">
            <p className="text-xs font-semibold text-purple-700 uppercase tracking-wide">Output</p>
            <p className="text-xl font-bold text-purple-900 mt-1">{metadata.output_tokens}</p>
            <p className="text-xs text-purple-600 mt-1">Tokens</p>
          </div>

          {/* Efficiency */}
          <div className="bg-orange-50 rounded-lg p-3 border border-orange-200 hover:border-orange-300 transition-colors">
            <p className="text-xs font-semibold text-orange-700 uppercase tracking-wide">Efficiency</p>
            <p className="text-xl font-bold text-orange-900 mt-1">{(metadata.output_tokens / metadata.input_tokens).toFixed(2)}</p>
            <p className="text-xs text-orange-600 mt-1">Ratio</p>
          </div>
        </div>
      ) : null}

      {/* Debug Toggle */}
      {metadata && (
        <div className="mt-3">
          <button
            onClick={() => setShowDebug(!showDebug)}
            className="text-xs font-semibold text-gray-600 hover:text-gray-900 uppercase tracking-wide cursor-pointer hover:underline"
          >
            {showDebug ? '✕ Hide Debug' : '⚙️ Show Debug'}
          </button>

          {/* Debug Info */}
          {showDebug && (
            <div className="mt-2 p-2 bg-gray-100 rounded border border-gray-300">
              <pre className="text-xs text-gray-700 font-mono overflow-auto max-h-24 bg-white p-2 rounded border border-gray-200">
                {JSON.stringify(metadata, null, 2)}
              </pre>
            </div>
          )}
        </div>
      )}
    </div>
  );
};