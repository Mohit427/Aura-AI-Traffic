const API_BASE_URL = "https://aura-backend-v27b.onrender.com";

export async function fetchLatestDecision() {
  const token = import.meta.env.VITE_CORA_TOKEN;

  const response = await fetch(`${API_BASE_URL}/api/latest-decision`, {
    method: "GET",
    headers: {
      Authorization: `Bearer ${token}`,
      "Content-Type": "application/json",
    },
  });

  if (!response.ok) {
    throw new Error(`Failed to fetch latest decision: ${response.status} ${response.statusText}`);
  }

  return response.json();
}
