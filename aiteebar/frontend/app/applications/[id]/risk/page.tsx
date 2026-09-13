'use client';

import { useEffect, useState } from 'react';
import { useParams } from 'next/navigation';
import axios from 'axios';
import PageHeader from '@/components/PageHeader';
import RiskScoreGauge from '@/components/risk/RiskScoreGauge';
import DimensionBreakdown from '@/components/risk/DimensionBreakdown';
import KeyConcernsList from '@/components/risk/KeyConcernsList';
import RecommendedControls from '@/components/risk/RecommendedControls';
import Loading from '@/components/common/Loading';

export default function RiskAssessmentPage() {
  const params = useParams() as { id: string };
  const applicationId = params?.id || '';

  const [riskAssessment, setRiskAssessment] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchRiskAssessment = async () => {
      try {
        setLoading(true);
        const response = await axios.get(
          `http://localhost:8000/api/risk/applications/${applicationId}`
        );
        setRiskAssessment(response.data);
        setError(null);
      } catch (err: any) {
        console.error('Error fetching risk assessment:', err);
        setError(err.response?.data?.detail || 'Failed to load risk assessment');
      } finally {
        setLoading(false);
      }
    };

    if (applicationId) {
      fetchRiskAssessment();
    }
  }, [applicationId]);

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

  if (!riskAssessment) {
    return (
      <div className="p-8 text-center">
        <p className="text-gray-600">No risk assessment data available</p>
      </div>
    );
  }

  return (
    <div className="space-y-8 p-6">
      <PageHeader
        title={riskAssessment.application_name}
        description="Risk Assessment & Security Evaluation"
        backHref="/applications"
      />

      {riskAssessment.is_demo && (
        <div className="p-3 bg-blue-50 border border-blue-200 rounded-lg">
          <p className="text-sm text-blue-800">
            ℹ️ This is demonstration data. Risk scores are calculated for illustrative purposes only.
          </p>
        </div>
      )}

      {/* Overall Risk Score */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <div>
          <RiskScoreGauge assessment={riskAssessment} />
        </div>
        <div className="space-y-4">
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-lg font-semibold mb-4">Assessment Summary</h2>
            <div className="space-y-3">
              <div className="flex justify-between">
                <span className="text-gray-600">Overall Risk Score:</span>
                <span className="font-semibold text-lg">{riskAssessment.overall_score}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Risk Level:</span>
                <span className={`font-semibold px-3 py-1 rounded-full text-sm ${
                  riskAssessment.risk_level === 'LOW' ? 'bg-green-100 text-green-800' :
                  riskAssessment.risk_level === 'MEDIUM' ? 'bg-yellow-100 text-yellow-800' :
                  riskAssessment.risk_level === 'HIGH' ? 'bg-orange-100 text-orange-800' :
                  'bg-red-100 text-red-800'
                }`}>
                  {riskAssessment.risk_level}
                </span>
              </div>
              <div className="flex justify-between text-sm text-gray-600">
                <span>Last Assessed:</span>
                <span>{new Date(riskAssessment.assessed_at).toLocaleDateString()}</span>
              </div>
              {riskAssessment.days_until_reassessment !== null && (
                <div className="flex justify-between text-sm text-gray-600">
                  <span>Next Assessment:</span>
                  <span>{riskAssessment.days_until_reassessment} days</span>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Dimension Breakdown */}
      <div>
        <DimensionBreakdown dimensions={riskAssessment.dimensions} />
      </div>

      {/* Key Concerns */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <div>
          <KeyConcernsList concerns={riskAssessment.key_concerns} />
        </div>
        <div>
          <RecommendedControls controls={riskAssessment.recommended_controls} />
        </div>
      </div>
    </div>
  );
}
