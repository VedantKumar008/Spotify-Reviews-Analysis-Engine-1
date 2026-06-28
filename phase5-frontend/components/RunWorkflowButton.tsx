interface RunWorkflowButtonProps {
  isRunning: boolean;
  onClick: () => void;
  label?: string;
}

export function RunWorkflowButton({
  isRunning,
  onClick,
  label = "Run Workflow",
}: RunWorkflowButtonProps) {
  return (
    <button
      type="button"
      onClick={onClick}
      disabled={isRunning}
      className="run-workflow-btn"
    >
      {isRunning ? (
        <>
          <span className="spinner" aria-hidden="true" />
          Starting workflow...
        </>
      ) : (
        label
      )}
    </button>
  );
}
