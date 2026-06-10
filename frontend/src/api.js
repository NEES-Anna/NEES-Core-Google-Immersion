const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

export async function analyzePrompt({ prompt, scenario }) {
  let response;

  try {
    response = await fetch(`${API_BASE_URL}/v1/guard/analyze`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ prompt, scenario }),
    });
  } catch {
    throw new Error("The NEES Core Engine API is temporarily unavailable. Please try again after the backend is online.");
  }

  if (!response.ok) {
    let message = `Request failed with ${response.status}`;
    try {
      const body = await response.json();
      message = body.detail?.[0]?.msg || body.detail || message;
    } catch {
      const detail = await response.text();
      message = detail || message;
    }
    throw new Error(message);
  }

  return response.json();
}
