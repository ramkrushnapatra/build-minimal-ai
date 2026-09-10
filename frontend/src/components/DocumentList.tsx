"use client";

import type { Document } from "@/types";
import { deleteDocument } from "@/lib/api";

interface Props {
  documents: Document[];
  selectedIds: Set<string>;
  onToggle: (id: string) => void;
  onRefresh: () => void;
}

const STATUS_COLORS: Record<string, string> = {
  pending: "text-yellow-400",
  processing: "text-blue-400",
  ready: "text-green-400",
  failed: "text-red-400",
};

export default function DocumentList({ documents, selectedIds, onToggle, onRefresh }: Props) {
  async function handleDelete(id: string) {
    await deleteDocument(id);
    onRefresh();
  }

  if (documents.length === 0) {
    return <p className="text-gray-500 text-sm">No documents uploaded yet.</p>;
  }

  return (
    <ul className="space-y-2">
      {documents.map((doc) => (
        <li
          key={doc.id}
          className="flex items-center gap-3 bg-surface-card border border-surface-border rounded-lg px-4 py-3"
        >
          <input
            type="checkbox"
            checked={selectedIds.has(doc.id)}
            disabled={doc.status !== "ready"}
            onChange={() => onToggle(doc.id)}
            className="accent-accent"
          />
          <div className="flex-1 min-w-0">
            <p className="text-sm font-medium truncate">{doc.filename}</p>
            <p className={`text-xs ${STATUS_COLORS[doc.status]}`}>{doc.status}</p>
          </div>
          <button
            onClick={() => handleDelete(doc.id)}
            className="text-gray-500 hover:text-red-400 text-xs"
          >
            Delete
          </button>
        </li>
      ))}
    </ul>
  );
}
