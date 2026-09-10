"use client";

import { useCallback, useEffect, useState } from "react";
import type { Document } from "@/types";
import { listDocuments } from "@/lib/api";
import DocumentUpload from "@/components/DocumentUpload";
import DocumentList from "@/components/DocumentList";
import ChatPanel from "@/components/ChatPanel";

export default function Home() {
  const [documents, setDocuments] = useState<Document[]>([]);
  const [selectedIds, setSelectedIds] = useState<Set<string>>(new Set());

  const refresh = useCallback(async () => {
    const docs = await listDocuments();
    setDocuments(docs);
    setSelectedIds((prev) => {
      const ready = new Set(docs.filter((d) => d.status === "ready").map((d) => d.id));
      return new Set([...prev].filter((id) => ready.has(id)));
    });
  }, []);

  useEffect(() => {
    refresh();
  }, [refresh]);

  function toggleDoc(id: string) {
    setSelectedIds((prev) => {
      const next = new Set(prev);
      if (next.has(id)) next.delete(id);
      else next.add(id);
      return next;
    });
  }

  return (
    <div className="flex h-screen">
      <aside className="w-80 border-r border-surface-border flex flex-col">
        <div className="p-4 border-b border-surface-border">
          <h1 className="text-lg font-bold">build-minimal-ai</h1>
          <p className="text-xs text-gray-400 mt-1">Document Q&A with RAG</p>
        </div>
        <div className="p-4 space-y-4 flex-1 overflow-y-auto">
          <DocumentUpload onUploaded={refresh} />
          <div>
            <h2 className="text-sm font-medium text-gray-400 mb-2">Documents</h2>
            <DocumentList
              documents={documents}
              selectedIds={selectedIds}
              onToggle={toggleDoc}
              onRefresh={refresh}
            />
          </div>
        </div>
      </aside>

      <main className="flex-1 flex flex-col">
        <div className="p-4 border-b border-surface-border">
          <p className="text-sm text-gray-400">
            {selectedIds.size > 0
              ? `Searching ${selectedIds.size} selected document(s)`
              : "Searching all ready documents"}
          </p>
        </div>
        <ChatPanel selectedDocumentIds={[...selectedIds]} />
      </main>
    </div>
  );
}
