import React from 'react';

interface RecommendedControlsProps {
  controls: string[];
}

export default function RecommendedControls({ controls }: RecommendedControlsProps) {
  const getControlIcon = (control: string) => {
    if (control.includes('monitor') || control.includes('audit')) return '📊';
    if (control.includes('encrypt') || control.includes('encryption')) return '🔐';
    if (control.includes('access') || control.includes('permission')) return '🔑';
    if (control.includes('SSO') || control.includes('SAML')) return '🔓';
    if (control.includes('incident')) return '🚨';
    if (control.includes('delete') || control.includes('retention')) return '🗑️';
    if (control.includes('DLP')) return '🛡️';
    if (control.includes('limit') || control.includes('rate')) return '⚙️';
    if (control.includes('review') || control.includes('assessment')) return '✓';
    return '→';
  };

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <div className="flex items-center gap-2 mb-6">
        <div className="text-2xl">✓</div>
        <h2 className="text-lg font-semibold">Recommended Controls</h2>
      </div>

      {controls && controls.length > 0 ? (
        <div className="space-y-3">
          {controls.map((control, index) => (
            <div
              key={index}
              className="flex gap-3 p-3 bg-green-50 border-l-4 border-green-400 rounded"
            >
              <div className="text-lg flex-shrink-0">{getControlIcon(control)}</div>
              <p className="text-gray-700 text-sm">{control}</p>
            </div>
          ))}
        </div>
      ) : (
        <div className="p-4 bg-gray-50 border border-gray-200 rounded">
          <p className="text-gray-700 text-sm">No specific controls recommended at this time</p>
        </div>
      )}

      {/* Implementation guidance */}
      <div className="mt-6 pt-4 border-t border-gray-200">
        <h3 className="font-semibold text-sm text-gray-900 mb-2">Implementation Priority</h3>
        <div className="space-y-2 text-xs text-gray-600">
          <div className="flex items-start gap-2">
            <span className="font-semibold text-red-600">Priority 1:</span>
            <span>Implement controls related to HIGH and CRITICAL risk dimensions</span>
          </div>
          <div className="flex items-start gap-2">
            <span className="font-semibold text-yellow-600">Priority 2:</span>
            <span>Address MEDIUM risk areas within the next quarter</span>
          </div>
          <div className="flex items-start gap-2">
            <span className="font-semibold text-green-600">Priority 3:</span>
            <span>Review and enhance LOW risk items as part of ongoing hardening</span>
          </div>
        </div>
      </div>
    </div>
  );
}
