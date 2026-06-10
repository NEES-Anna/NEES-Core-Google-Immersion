export default function TracePanel({ trace }) {
  return (
    <article className="result-card trace-card">
      <h2>Trace JSON</h2>
      <p className="trace-helper">Every decision includes a trace ID for audit and debugging.</p>
      <pre>{JSON.stringify(trace, null, 2)}</pre>
    </article>
  );
}
