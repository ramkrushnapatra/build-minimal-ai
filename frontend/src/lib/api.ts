import type { Citation, Document, Job } from "@/types";

const API_BASE = "/api";

export async function listDocuments(): Promise<Document[]> {
  const res = await fetch(`${API_BASE}/documents`);
  if (!res.ok) throw new Error("Failed to fetch documents");
  return res.json();
}

export async function uploadDocument(file: File): Promise<Document> {
  const form = new FormData();
  form.append("file", file);
  const res = await fetch(`${API_BASE}/documents/upload`, { method: "POST", body: form });
  if (!res.ok) throw new Error("Upload failed");
  return res.json();
}

export async function ingestDocument(documentId: string): Promise<Job> {
  const res = await fetch(`${API_BASE}/documents/${documentId}/ingest`, { method: "POST" });
  if (!res.ok) throw new Error("Failed to start ingestion");
  return res.json();
}

export async function getJob(jobId: string): Promise<Job> {
  const res = await fetch(`${API_BASE}/jobs/${jobId}`);
  if (!res.ok) throw new Error("Failed to fetch job");
  return res.json();
}

export async function deleteDocument(documentId: string): Promise<void> {
  const res = await fetch(`${API_BASE}/documents/${documentId}`, { method: "DELETE" });
  if (!res.ok) throw new Error("Failed to delete document");
}

export async function streamChat(
  message: string,
  documentIds: string[] | null,
  onToken: (token: string) => void,
  onCitations: (citations: Citation[]) => void,
  onDone: () => void,
  onError: (err: string) => void,
) {
  const res = await fetch(`${API_BASE}/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json", Accept: "text/event-stream" },
    body: JSON.stringify({ message, document_ids: documentIds }),
  });

  if (!res.ok || !res.body) {
    onError("Chat request failed");
    return;
  }

  const reader = res.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;

    buffer += decoder.decode(value, { stream: true });
    const lines = buffer.split("\n");
    buffer = lines.pop() || "";

    let eventType = "";
    for (const line of lines) {
      if (line.startsWith("event:")) {
        eventType = line.slice(6).trim();
      } else if (line.startsWith("data:") && eventType) {
        const data = line.slice(5).trim();
        if (eventType === "token") {
          onToken(JSON.parse(data));
        } else if (eventType === "citations") {
          onCitations(JSON.parse(data));
        } else if (eventType === "done") {
          onDone();
        }
        eventType = "";
      }
    }
  }
  onDone();
}
