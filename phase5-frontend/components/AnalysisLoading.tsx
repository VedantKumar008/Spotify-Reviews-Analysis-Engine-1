interface AnalysisLoadingProps {
  progress: number;
  currentStep: string;
}

const WORKFLOW_PHASES = [
  "Reviews Ingestion",
  "Data Cleaning",
  "LLM Analysis",
];

function getActivePhase(progress: number): number {
  if (progress < 34) return 0;
  if (progress < 67) return 1;
  return 2;
}

export function AnalysisLoading({ progress, currentStep }: AnalysisLoadingProps) {
  const activePhase = getActivePhase(progress);

  return (
    <div className="page-shell flex items-center justify-center">
      <div className="loading-panel">
        <div className="loading-spinner" aria-hidden="true" />
        <h2 className="loading-title">Running analysis workflow</h2>
        <p className="loading-subtitle">{currentStep || "Preparing your insights..."}</p>

        <div className="workflow-track workflow-track--compact">
          {WORKFLOW_PHASES.map((phase, index) => (
            <div
              key={phase}
              className={`loading-phase ${index <= activePhase ? "loading-phase--active" : ""}`}
            >
              <span className="loading-phase-dot" />
              <span className="loading-phase-label">{phase}</span>
            </div>
          ))}
        </div>

        <div className="progress-track">
          <div className="progress-fill" style={{ width: `${progress}%` }} />
        </div>
        <p className="progress-label">{Math.round(progress)}% complete</p>
      </div>
    </div>
  );
}
