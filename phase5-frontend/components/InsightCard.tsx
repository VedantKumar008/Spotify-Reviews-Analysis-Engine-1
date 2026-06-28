import { formatAnswer } from "@/lib/formatAnswer";

interface InsightCardProps {
  index: number;
  question: string;
  answer: string;
}

export function InsightCard({ index, question, answer }: InsightCardProps) {
  const formattedAnswer = formatAnswer(answer);

  return (
    <article className="insight-card">
      <p className="insight-index">Insight {index}</p>
      <h3 className="insight-question">{question}</h3>
      <p className="insight-answer">{formattedAnswer}</p>
    </article>
  );
}
