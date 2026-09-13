import React from 'react';

interface KeyConcernsListProps {
  concerns: string[];
}

export default function KeyConcernsList({ concerns }: KeyConcernsListProps) {
  return (
    <div className="bg-white rounded-lg shadow p-6">
      <div className="flex items-center gap-2 mb-6">
        <div className="text-2xl">⚠️</div>
        <h2 className="text-lg font-semibold">Key Concerns</h2>
      </div>

      {concerns && concerns.length > 0 ? (
        <div className="space-y-3">
          {concerns.map((concern, index) => (
            <div
              key={index}
              className="flex gap-3 p-3 bg-orange-50 border-l-4 border-orange-400 rounded"
            >
              <div className="text-orange-600 flex-shrink-0 mt-0.5">•</div>
              <p className="text-gray-700 text-sm">{concern}</p>
            </div>
          ))}
        </div>
      ) : (
        <div className="p-4 bg-green-50 border border-green-200 rounded">
          <p className="text-green-800 text-sm">✓ No critical concerns identified</p>
        </div>
      )}

      {/* Risk assessment note */}
      <div className="mt-6 pt-4 border-t border-gray-200">
        <h3 className="font-semibold text-sm text-gray-900 mb-2">What are key concerns?</h3>
        <p className="text-xs text-gray-600">
          Key concerns highlight important risk factors identified during the assessment.
          These should be addressed through appropriate security controls and vendor engagement.
        </p>
      </div>
    </div>
  );
}
