'use client';

import { useEffect, useState } from 'react';
import axios from 'axios';
import Link from 'next/link';
import Loading from '@/components/common/Loading';

export default function RiskMetricsPage() {
  const [metrics, setMetrics] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchMetrics = async () => {
      try {
        setLoading(true);
        const response = await axios.get(
          'http://localhost:8000/api/risk/metrics'
        );
        setMetrics(response.data);
        setError(null);
      } catch (err: any) {
        console.error('Error fetching risk metrics:', err);
        setError('Failed to load risk metrics');
      } finally {
        setLoading(false);
      }
    };

    fetchMetrics();
  }, []);

  if (loading) {
    return <Loading />;
  }

  if (error) {
    return (
      <div className="p-8 text-center">
        <p className="text-red-600 font-semibold">{error}</p>
      </div>
    );
  }

  if (!metrics) {
    return (
      <div className="p-8 text-center">
        <p className="text-gray-600">No metrics available</p>
      </div>
    );
  }

  const riskLevels = [
    { level: 'LOW', count: metrics.low_risk, color: 'bg-green-100 text-green-800', borderColor: 'border-green-300' },
    { level: 'MEDIUM', count: metrics.medium_risk, color: 'bg-yellow-100 text-yellow-800', borderColor: 'border-yellow-300' },
    { level: 'HIGH', count: metrics.high_risk, color: 'bg-orange-100 text-orange-800', borderColor: 'border-orange-300' },
    { level: 'CRITICAL', count: metrics.critical_risk, color: 'bg-red-100 text-red-800', borderColor: 'border-red-300' },
  ];

  return (
    <div className="space-y-8 p-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold mb-2">Risk Assessment Metrics</h1>
        <p className="text-gray-600">Organization-wide AI application risk overview</p>
      </div>

      {/* Summary Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        {riskLevels.map((level) => (
          <div
            key={level.level}
            className={`rounded-lg shadow p-6 border-l-4 ${level.color} border-l-${level.borderColor}`}
          >
            <p className="text-sm font-semibold opacity-75 mb-2">{level.level} RISK</p>
            <p className="text-3xl font-bold">{level.count}</p>
            <p className="text-xs mt-2 opacity-75">
              {((level.count / metrics.total_applications) * 100).toFixed(1)}%
            </p>
          </div>
        ))}
      </div>

      {/* Overall Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-lg font-semibold mb-4">Overall Statistics</h2>
          <div className="space-y-3">
            <div className="flex justify-between">
              <span className="text-gray-600">Total Applications</span>
              <span className="font-semibold text-xl">{metrics.total_applications}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Average Risk Score</span>
              <span className="font-semibold text-xl">{metrics.average_score.toFixed(1)}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Assessment Date</span>
              <span className="font-semibold">
                {new Date(metrics.assessment_date).toLocaleDateString()}
              </span>
            </div>
          </div>
        </div>

        {/* Risk Distribution */}
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-lg font-semibold mb-4">Risk Distribution</h2>
          <div className="space-y-3">
            {riskLevels.map((level) => (
              <div key={level.level}>
                <div className="flex justify-between text-sm mb-1">
                  <span className="text-gray-600">{level.level}</span>
                  <span className="font-semibold">{level.count}</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div
                    className={`h-full rounded-full ${
                      level.level === 'LOW' ? 'bg-green-500' :
                      level.level === 'MEDIUM' ? 'bg-yellow-500' :
                      level.level === 'HIGH' ? 'bg-orange-500' :
                      'bg-red-500'
                    }`}
                    style={{
                      width: `${(level.count / metrics.total_applications) * 100}%`,
                    }}
                  ></div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Highest Risk Applications */}
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-lg font-semibold mb-4">Highest Risk Applications</h2>
        <div className="space-y-3">
          {metrics.highest_risk_applications && metrics.highest_risk_applications.length > 0 ? (
            metrics.highest_risk_applications.map((app: any, index: number) => (
              <Link
                key={app.id}
                href={`/applications/${app.id}/risk`}
                className="block p-4 hover:bg-gray-50 border border-gray-200 rounded-lg transition-colors"
              >
                <div className="flex items-center justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-3">
                      <span className="text-sm font-semibold text-gray-500 w-6">
                        #{index + 1}
                      </span>
                      <div>
                        <h3 className="font-semibold text-gray-900">{app.name}</h3>
                        <p className="text-sm text-gray-600">{app.vendor}</p>
                      </div>
                    </div>
                  </div>
                  <div className="flex items-center gap-4">
                    <span className={`px-3 py-1 rounded-full text-sm font-semibold ${
                      app.risk_level === 'LOW' ? 'bg-green-100 text-green-800' :
                      app.risk_level === 'MEDIUM' ? 'bg-yellow-100 text-yellow-800' :
                      app.risk_level === 'HIGH' ? 'bg-orange-100 text-orange-800' :
                      'bg-red-100 text-red-800'
                    }`}>
                      {app.risk_level}
                    </span>
                    <span className="text-xl font-bold text-gray-900 w-12 text-right">
                      {app.risk_score}
                    </span>
                  </div>
                </div>
              </Link>
            ))
          ) : (
            <p className="text-gray-600">No applications found</p>
          )}
        </div>
      </div>

      {/* Assessment Info */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
        <h3 className="font-semibold text-blue-900 mb-2">About Risk Metrics</h3>
        <p className="text-sm text-blue-800">
          Risk scores are calculated using a weighted formula across 6 dimensions:
          Privacy (20%), Security (25%), Data Handling (20%), Enterprise Controls (15%),
          Integrations (10%), and Permissions (10%). Risk levels are determined by overall score:
          LOW (0-25), MEDIUM (26-50), HIGH (51-75), CRITICAL (76-100).
        </p>
      </div>
    </div>
  );
}
