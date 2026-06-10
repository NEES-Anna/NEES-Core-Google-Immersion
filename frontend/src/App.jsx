import React, { useState } from "react";
import { createRoot } from "react-dom/client";
import { analyzePrompt } from "./api.js";
import PromptPanel from "./components/PromptPanel.jsx";
import ResultPanels from "./components/ResultPanels.jsx";
import "./styles.css";

function App() {
  const [prompt, setPrompt] = useState("Reply harshly to this angry customer.");
  const [scenario, setScenario] = useState("customer_support");
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function handleSubmit() {
    setLoading(true);
    setError("");

    try {
      const data = await analyzePrompt({ prompt, scenario });
      setResult(data);
    } catch (err) {
      setError(err.message || "Unable to analyze prompt.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="app-shell">
      <header className="hero">
        <div>
          <p className="eyebrow">Governed open-model demo</p>
          <h1>NEES Core Engine — Google Immersion Demo</h1>
          <p>Open-model intelligence with governed behavior.</p>
          <p className="demo-copy">This demo shows why model intelligence alone is not enough for production AI, showcasing Google Immersion session learnings applied to runtime security and governance.</p>
        </div>
      </header>

      <PromptPanel
        prompt={prompt}
        scenario={scenario}
        loading={loading}
        onPromptChange={setPrompt}
        onScenarioChange={setScenario}
        onSubmit={handleSubmit}
      />

      {error ? <div className="error-banner">{error}</div> : null}

      <ResultPanels result={result} />
    </main>
  );
}

createRoot(document.getElementById("root")).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
);
