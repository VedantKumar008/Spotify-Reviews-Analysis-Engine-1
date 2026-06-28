interface WorkflowStepProps {
  step: number;
  title: string;
  icon: React.ReactNode;
}

export function WorkflowStep({ step, title, icon }: WorkflowStepProps) {
  return (
    <div className="flex flex-col items-center flex-1 min-w-[140px] max-w-[220px]">
      <div className="workflow-card w-full">
        <div className="workflow-step-badge">{step}</div>
        <div className="workflow-icon">{icon}</div>
        <h3 className="workflow-title">{title}</h3>
      </div>
    </div>
  );
}
