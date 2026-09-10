export async function fetchItems() {
  const res = await fetch("/items");
  if (!res.ok) throw new Error("Failed to load items");
  return res.json();
}

export async function ingestNote(content) {
  const res = await fetch("/ingest", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ type: "note", content }),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || "Failed to save note");
  }
  return res.json();
}

export async function ingestUrl(url) {
  const res = await fetch("/ingest", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ type: "url", url }),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || "Failed to save URL");
  }
  return res.json();
}

export async function askQuestion(question) {
  const res = await fetch("/query", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ question }),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || "Query failed");
  }
  return res.json();
}
