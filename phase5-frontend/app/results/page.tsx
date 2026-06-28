import { Suspense } from "react";
import { ResultsContent } from "./ResultsContent";

function ResultsFallback() {
  return (
    <div className="page-shell flex items-center justify-center">
      <div className="loading-panel">
        <div className="loading-spinner" aria-hidden="true" />
        <h2 className="loading-title">Loading results</h2>
      </div>
    </div>
  );
}

export default function ResultsPage() {
  return (
    <Suspense fallback={<ResultsFallback />}>
      <ResultsContent />
    </Suspense>
  );
}
