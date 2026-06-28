import { formatDuration } from "@/lib/formatDuration";

interface ResultsSummaryProps {
  reviewsAnalyzed: number;
  processingTimeSeconds: number;
  resultsSource?: string;
}

export function ResultsSummary({
  reviewsAnalyzed,
  processingTimeSeconds,
  resultsSource,
}: ResultsSummaryProps) {
  const usingOfflineResults = resultsSource === "precomputed_offline";

  return (
    <div className="summary-card">
      <p className="summary-eyebrow">Derived from real Spotify reviews on Google Play</p>
      {usingOfflineResults && (
        <p className="summary-warning">
          Live AI analysis is unavailable because the Groq API key is invalid. Showing
          pre-computed insights from an earlier successful run.
        </p>
      )}
      <div className="summary-grid">
        <div>
          <p className="summary-label">Reviews analyzed</p>
          <p className="summary-value">{reviewsAnalyzed.toLocaleString()}</p>
        </div>
        <div>
          <p className="summary-label">Processing time</p>
          <p className="summary-value">{formatDuration(processingTimeSeconds)}</p>
        </div>
      </div>
    </div>
  );
}
