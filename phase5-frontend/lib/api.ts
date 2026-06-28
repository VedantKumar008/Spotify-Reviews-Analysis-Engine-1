export interface WorkflowResult {
  question: string;
  answer: string;
  cached: boolean;
  reviews_analyzed: number;
}

export interface AnalysisResults {
  generated_at: string;
  model_used: string;
    statistics: {
    total_reviews_analyzed: number;
    total_api_calls: number;
    cache_hits: number;
    cache_misses: number;
    total_tokens_used: number;
    analysis_time_seconds: number;
    results_source?: string;
    api_key_valid?: boolean;
  };
  results: {
    q1: WorkflowResult;
    q2: WorkflowResult;
    q3: WorkflowResult;
    q4: WorkflowResult;
    q5: WorkflowResult;
    q6: WorkflowResult;
  };
}

export interface WorkflowStatus {
  workflow_id: string;
  status: "pending" | "running" | "completed" | "failed";
  progress: number;
  current_step: string;
  error?: string;
}

export async function startWorkflow(): Promise<{ workflow_id: string }> {
  const response = await fetch("/api/run-workflow", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ use_cache: true, use_all_reviews: true }),
  });

  if (!response.ok) {
    throw new Error("Failed to start workflow");
  }

  return response.json();
}

export async function getWorkflowStatus(
  workflowId: string
): Promise<WorkflowStatus> {
  const response = await fetch(`/api/status/${workflowId}`);
  if (!response.ok) {
    throw new Error("Failed to fetch workflow status");
  }
  return response.json();
}

export async function getWorkflowResults(workflowId: string): Promise<{
  results: AnalysisResults;
}> {
  const response = await fetch(`/api/results/${workflowId}`);
  if (!response.ok) {
    throw new Error("Failed to fetch results");
  }
  const data = await response.json();
  return { results: data.results };
}
