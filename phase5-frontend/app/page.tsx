"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { WorkflowVisualization } from "@/components/WorkflowVisualization";
import { RunWorkflowButton } from "@/components/RunWorkflowButton";
import { startWorkflow } from "@/lib/api";

export default function Home() {
  const [isRunning, setIsRunning] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const router = useRouter();

  const handleRunWorkflow = async () => {
    setIsRunning(true);
    setError(null);

    try {
      const data = await startWorkflow();
      router.push(`/results?workflowId=${data.workflow_id}`);
    } catch {
      setError("Unable to start the workflow. Please try again.");
      setIsRunning(false);
    }
  };

  return (
    <div className="page-shell">
      <main className="landing-main">
        <header className="landing-header">
          <p className="landing-eyebrow">Spotify Reviews Analysis Engine</p>
          <h1 className="landing-title">
            Turn user feedback into product insights
          </h1>
          <p className="landing-description">
            A simple workflow that transforms real Spotify reviews into clear,
            actionable research answers.
          </p>
        </header>

        <section className="landing-workflow" aria-label="Analysis workflow">
          <WorkflowVisualization />
        </section>

        <div className="landing-action">
          <RunWorkflowButton isRunning={isRunning} onClick={handleRunWorkflow} />
          {error && <p className="error-message">{error}</p>}
        </div>
      </main>
    </div>
  );
}
