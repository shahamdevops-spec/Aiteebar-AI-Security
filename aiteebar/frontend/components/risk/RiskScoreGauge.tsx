import React from 'react';

interface RiskScoreGaugeProps {
  assessment: any;
}

export default function RiskScoreGauge({ assessment }: RiskScoreGaugeProps) {
  const score = assessment.overall_score;
  const riskColor = assessment.risk_color;

  // Calculate rotation for gauge (0-180 degrees)
  const rotation = (score / 100) * 180 - 90;

  const getRiskLevelColor = (level: string) => {
    switch (level) {
      case 'LOW':
        return '#10b981'; // green
      case 'MEDIUM':
        return '#f59e0b'; // amber
      case 'HIGH':
        return '#ef5350'; // orange
      case 'CRITICAL':
        return '#dc2626'; // red
      default:
        return '#6b7280';
    }
  };

  return (
    <div className="bg-white rounded-lg shadow p-8">
      <h2 className="text-lg font-semibold mb-8 text-center">Overall Risk Score</h2>

      <div className="flex flex-col items-center justify-center">
        {/* SVG Gauge */}
        <svg width="280" height="160" viewBox="0 0 280 160" className="mb-6">
          {/* Background arc */}
          <defs>
            <linearGradient id="gaugeGradient" x1="0%" y1="0%" x2="100%" y2="0%">
              <stop offset="0%" stopColor="#10b981" />
              <stop offset="33%" stopColor="#f59e0b" />
              <stop offset="66%" stopColor="#ef5350" />
              <stop offset="100%" stopColor="#dc2626" />
            </linearGradient>
          </defs>

          {/* Gradient arc background */}
          <path
            d="M 40 140 A 100 100 0 0 1 240 140"
            stroke="url(#gaugeGradient)"
            strokeWidth="12"
            fill="none"
            opacity="0.3"
          />

          {/* Main arc */}
          <path
            d="M 40 140 A 100 100 0 0 1 240 140"
            stroke={getRiskLevelColor(assessment.risk_level)}
            strokeWidth="12"
            fill="none"
            strokeDasharray={`${(score / 100) * (Math.PI * 100)} ${Math.PI * 100}`}
            strokeLinecap="round"
          />

          {/* Needle */}
          <g transform={`rotate(${rotation} 140 140)`}>
            <circle cx="140" cy="140" r="6" fill="#1f2937" />
            <line
              x1="140"
              y1="140"
              x2="140"
              y2="50"
              stroke="#1f2937"
              strokeWidth="3"
              strokeLinecap="round"
            />
          </g>

          {/* Center circle */}
          <circle cx="140" cy="140" r="15" fill="white" stroke="#1f2937" strokeWidth="2" />
        </svg>

        {/* Score display */}
        <div className="text-center">
          <p className="text-5xl font-bold" style={{ color: getRiskLevelColor(assessment.risk_level) }}>
            {score}
          </p>
          <p className="text-gray-600 text-sm mt-2">Risk Score (0-100)</p>
        </div>

        {/* Risk level badge */}
        <div className="mt-6">
          <span className={`px-4 py-2 rounded-full font-semibold text-white ${
            assessment.risk_level === 'LOW' ? 'bg-green-500' :
            assessment.risk_level === 'MEDIUM' ? 'bg-yellow-500' :
            assessment.risk_level === 'HIGH' ? 'bg-orange-500' :
            'bg-red-500'
          }`}>
            {assessment.risk_level} RISK
          </span>
        </div>
      </div>

      {/* Legend */}
      <div className="mt-8 pt-6 border-t border-gray-200">
        <div className="grid grid-cols-2 gap-4 text-sm">
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 rounded-full bg-green-500"></div>
            <span className="text-gray-600">0-25: Low Risk</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 rounded-full bg-yellow-500"></div>
            <span className="text-gray-600">26-50: Medium Risk</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 rounded-full bg-orange-500"></div>
            <span className="text-gray-600">51-75: High Risk</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 rounded-full bg-red-500"></div>
            <span className="text-gray-600">76-100: Critical Risk</span>
          </div>
        </div>
      </div>
    </div>
  );
}
