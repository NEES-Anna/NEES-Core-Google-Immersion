import RiskBadge from "./RiskBadge.jsx";
import TracePanel from "./TracePanel.jsx";

export default function ResultPanels({ result }) {
  if (!result) {
    return (
      <section className="empty-state">
        <h2>Awaiting analysis</h2>
        <p>Submit a prompt to see raw model output, policy analysis, governed response, and audit trace.</p>
      </section>
    );
  }

  const mockMode = Boolean(result.trace?.mock_mode);

  return (
    <>
      <div className={`mode-banner ${mockMode ? "mode-mock" : "mode-live"}`}>
        {mockMode ? "Mock Demo Mode" : "Live Model Candidate"}
      </div>

      <section className="results-grid" aria-label="Analysis results">
        <article className="result-card">
          <div className="card-title-row">
            <h2>Model Candidate Response</h2>
            <span className={`mode-pill ${mockMode ? "mode-mock" : "mode-live"}`}>
              {mockMode ? "Mock Demo Mode" : "Live Model Candidate"}
            </span>
          </div>
          <pre>{result.gemma_raw_response}</pre>
        </article>

        <article className="result-card">
          <div className="card-title-row">
            <h2>NEES Governance Analysis</h2>
            <RiskBadge risk={result.risk_band} />
          </div>
          <dl className="analysis-list">
            <div>
              <dt>Intent</dt>
              <dd>{result.intent}</dd>
            </div>
            <div>
              <dt>Policy</dt>
              <dd>{result.policy_decision}</dd>
            </div>
            <div>
              <dt>Flags</dt>
              <dd>{result.flags.length ? result.flags.join(", ") : "none"}</dd>
            </div>
            <div>
              <dt>Trace ID</dt>
              <dd>{result.trace_id}</dd>
            </div>
          </dl>
          <p className="explanation">{result.explanation}</p>
        </article>

        <article className="result-card governed">
          <h2>Governed Response</h2>
          <p className="governed-response">{result.governed_response}</p>
        </article>

        <TracePanel trace={result.trace} />
      </section>
    </>
  );
}
