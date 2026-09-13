import Link from 'next/link';

interface RiskBadgeProps {
  applicationId: string;
  riskScore: number;
  riskLevel: string;
  compact?: boolean;
}

export default function RiskBadge({
  applicationId,
  riskScore,
  riskLevel,
  compact = false,
}: RiskBadgeProps) {
  const getRiskColor = (level: string) => {
    switch (level) {
      case 'LOW':
        return 'bg-green-100 text-green-800 border-green-300';
      case 'MEDIUM':
        return 'bg-yellow-100 text-yellow-800 border-yellow-300';
      case 'HIGH':
        return 'bg-orange-100 text-orange-800 border-orange-300';
      case 'CRITICAL':
        return 'bg-red-100 text-red-800 border-red-300';
      default:
        return 'bg-gray-100 text-gray-800 border-gray-300';
    }
  };

  const getRiskIcon = (level: string) => {
    switch (level) {
      case 'LOW':
        return '✓';
      case 'MEDIUM':
        return '⚠';
      case 'HIGH':
        return '⚠️';
      case 'CRITICAL':
        return '🚨';
      default:
        return '•';
    }
  };

  if (compact) {
    return (
      <Link href={`/applications/${applicationId}/risk`}>
        <span className={`inline-flex items-center gap-2 px-3 py-1 rounded-full text-sm font-semibold border ${getRiskColor(riskLevel)} hover:opacity-80 transition-opacity cursor-pointer`}>
          <span>{getRiskIcon(riskLevel)}</span>
          <span>{riskScore}</span>
          <span className="text-xs">({riskLevel})</span>
        </span>
      </Link>
    );
  }

  return (
    <Link href={`/applications/${applicationId}/risk`}>
      <div className={`p-4 rounded-lg border-2 cursor-pointer hover:shadow-md transition-shadow ${getRiskColor(riskLevel)}`}>
        <div className="flex items-center justify-between">
          <div>
            <p className="text-xs font-semibold opacity-75">Risk Score</p>
            <p className="text-2xl font-bold mt-1">{riskScore}</p>
          </div>
          <div className="text-4xl opacity-30">{getRiskIcon(riskLevel)}</div>
        </div>
        <div className="mt-3 pt-3 border-t border-current border-opacity-20">
          <p className="text-xs font-semibold">{riskLevel} RISK</p>
          <p className="text-xs opacity-75 mt-1">View detailed assessment →</p>
        </div>
      </div>
    </Link>
  );
}
