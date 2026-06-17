const BASE = 'http://localhost:8000';

export async function chat(workspace_id: string, query: string) {
  const resp = await fetch(`${BASE}/api/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ workspace_id, query })
  });
  return resp.json();
}

export async function providers() {
  const resp = await fetch(`${BASE}/api/settings/providers`);
  return resp.json();
}
