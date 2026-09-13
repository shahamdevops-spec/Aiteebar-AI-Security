import React from 'react';

interface Dimension {
  dimension: string;
  score: number;
  color: string;
  label: string;
  explanation: string;
}

interface DimensionBreakdownProps {
  dimensions: Dimension[];
}

export default function DimensionBreakdown({ dimensions }: DimensionBreakdownProps) {
  const colorMap = {
    green: '#10b981',
    yellow: '#f59e0b',
    orange: '#ef5350',
    red: '#dc2626',
  };

  const getColorClass = (color: string) => {
    switch (color) {
      case 'green':
        return 'bg-green-500';
      case 'yellow':
        return 'bg-yellow-500';
      case 'orange':
        return 'bg-orange-500';
      case 'red':
        return 'bg-red-500';
      default:
        return 'bg-gray-500';
    }
  };

  const formatDimensionName = (name: string) => {
    return name
      .replace(/_/g, ' ')
      .split(' ')
      .map(word => word.charAt(0).toUpperCase() + word.slice(1))
      .join(' ');
  };

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <h2 className="text-lg font-semibold mb-6">Risk Dimension Breakdown</h2>

      <div className="space-y-6">
        {dimensions.map((dim) => (
          <div key={dim.dimension}>
            {/* Dimension header */}
            <div className="flex justify-between items-start mb-2">
              <div>
                <h3 className="font-semibold text-gray-900">
                  {formatDimensionName(dim.dimension)}
                </h3>
                <p className="text-sm text-gray-600 mt-1">{dim.explanation}</p>
              </div>
              <div className="text-right">
                <p className="text-2xl font-bold" style={{ color: colorMap[dim.color as keyof typeof colorMap] }}>
                  {dim.score}
                </p>
                <p className="text-xs text-gray-600">{dim.label}</p>
              </div>
            </div>

            {/* Progress bar */}
            <div className="w-full bg-gray-200 rounded-full h-3 overflow-hidden">
              <div
                className={`h-full ${getColorClass(dim.color)} rounded-full transition-all duration-500`}
                style={{ width: `${dim.score}%` }}
              ></div>
            </div>
          </div>
        ))}
      </div>

      {/* Summary table */}
      <div className="mt-8 pt-6 border-t border-gray-200">
        <h3 className="font-semibold mb-4">Quick Summary</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {dimensions.map((dim) => (
            <div key={`summary-${dim.dimension}`} className="p-3 bg-gray-50 rounded">
              <div className="flex justify-between items-center">
                <span className="text-sm font-medium text-gray-700">
                  {formatDimensionName(dim.dimension)}
                </span>
                <div className="flex items-center gap-2">
                  <div
                    className="w-3 h-3 rounded-full"
                    style={{ backgroundColor: colorMap[dim.color as keyof typeof colorMap] }}
                  ></div>
                  <span className="font-semibold text-sm">{dim.score}</span>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Score interpretation */}
      <div className="mt-6 p-4 bg-blue-50 border border-blue-200 rounded-lg">
        <h4 className="font-semibold text-sm text-blue-900 mb-2">Score Interpretation</h4>
        <p className="text-sm text-blue-800">
          Higher scores indicate higher risk. Each dimension evaluates a specific aspect of the application's security and privacy posture. Review dimensions with scores above 70 for immediate attention.
        </p>
      </div>
    </div>
  );
}
