export function formatAnswer(answer: string): string {
  return answer
    .replace(/\*\*/g, "")
    .replace(/^[*•-]\s+/gm, "")
    .replace(/\n{3,}/g, "\n\n")
    .trim();
}
