// Thin fetch wrapper around the three backend endpoints.
const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

async function handleResponse(response) {
  if (!response.ok) {
    const body = await response.json().catch(() => ({}));
    throw new Error(body.detail || `Request failed (${response.status})`);
  }
  return response.json();
}

export async function createEntry(text) {
  const response = await fetch(`${API_URL}/entries`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ text }),
  });
  return handleResponse(response);
}

export async function getEntries() {
  const response = await fetch(`${API_URL}/entries`);
  return handleResponse(response);
}

export async function getEntry(id) {
  const response = await fetch(`${API_URL}/entries/${id}`);
  return handleResponse(response);
}
