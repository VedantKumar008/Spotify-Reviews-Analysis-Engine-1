"use client";

import { useEffect, useState } from "react";
import { useSearchParams, useRouter } from "next/navigation";
import { AnalysisLoading } from "@/components/AnalysisLoading";
import { InsightCard } from "@/components/InsightCard";
import { ResultsSummary } from "@/components/ResultsSummary";
import { RunWorkflowButton } from "@/components/RunWorkflowButton";
import {
  AnalysisResults,
  getWorkflowResults,
  getWorkflowStatus,
} from "@/lib/api";
import { RESEARCH_QUESTIONS } from "@/lib/questions";

export function ResultsContent() {
  const searchParams = useSearchParams();
  const router = useRouter();
  const workflowId = searchParams.get("workflowId");

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [results, setResults] = useState<AnalysisResults | null>(null);
  const [progress, setProgress] = useState(0);
  const [currentStep, setCurrentStep] = useState("");

  useEffect(() => {
    if (!workflowId) {
      router.push("/");
      return;
    }

    let cancelled = false;

    const pollResults = async () => {
      try {
        const statusData = await getWorkflowStatus(workflowId);

        if (cancelled) return;

        setProgress(statusData.progress);
        setCurrentStep(statusData.current_step);

        if (statusData.status === "completed") {
          const resultsData = await getWorkflowResults(workflowId);

          if (cancelled) return;

          const analysisResults = resultsData.results;

          if (!analysisResults?.statistics) {
            setError("Invalid results received from the analysis workflow.");
            setLoading(false);
            return;
          }

          setResults(analysisResults);
          setLoading(false);
        } else if (statusData.status === "failed") {
          setError(statusData.error || "The workflow failed. Please try again.");
          setLoading(false);
        } else {
          setTimeout(pollResults, 1500);
        }
      } catch {
        if (!cancelled) {
          setError("Failed to fetch workflow results.");
          setLoading(false);
        }
      }
    };

    pollResults();

    return () => {
      cancelled = true;
    };
  }, [workflowId, router]);

  if (error) {
    return (
      <div className="page-shell flex items-center justify-center">
        <div className="error-panel">
          <h1 className="error-title">Something went wrong</h1>
          <p className="error-copy">{error}</p>
          <RunWorkflowButton
            isRunning={false}
            onClick={() => router.push("/")}
            label="Try Again"
          />
        </div>
      </div>
    );
  }

  if (loading) {
    return <AnalysisLoading progress={progress} currentStep={currentStep} />;
  }

  if (!results) {
    return null;
  }

  return (
    <div className="page-shell">
      <main className="results-main">
        <header className="results-header">
          <p className="landing-eyebrow">Analysis complete</p>
          <h1 className="results-title">Product insights from Spotify reviews</h1>
          <p className="results-description">
            Six research questions answered from analyzed user feedback.
          </p>
        </header>

        <ResultsSummary
          reviewsAnalyzed={results.statistics.total_reviews_analyzed}
          processingTimeSeconds={results.statistics.analysis_time_seconds}
          resultsSource={results.statistics.results_source}
        />

        <section className="insights-list" aria-label="Research insights">
          {RESEARCH_QUESTIONS.map((item, index) => {
            const result = results.results[item.key];
            if (!result) return null;

            return (
              <InsightCard
                key={item.key}
                index={index + 1}
                question={item.label}
                answer={result.answer}
              />
            );
          })}
        </section>

        <div className="results-action">
          <RunWorkflowButton
            isRunning={false}
            onClick={() => router.push("/")}
            label="Run Again"
          />
        </div>
      </main>
    </div>
  );
}
