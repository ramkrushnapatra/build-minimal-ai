"use client";

import { useRef, useState } from "react";
import { ingestDocument, uploadDocument } from "@/lib/api";

interface Props {
  onUploaded: () => void;
}

export default function DocumentUpload({ onUploaded }: Props) {
  const inputRef = useRef<HTMLInputElement>(null);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleFile(file: File) {
    setUploading(true);
    setError(null);
    try {
      const doc = await uploadDocument(file);
      const job = await ingestDocument(doc.id);

      // Poll until ingestion completes
      const poll = async () => {
        const { getJob } = await import("@/lib/api");
        const status = await getJob(job.id);
        if (status.status === "completed" || status.status === "failed") {
          setUploading(false);
          onUploaded();
          return;
        }
        setTimeout(poll, 1500);
      };
      poll();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Upload failed");
      setUploading(false);
    }
  }

  return (
    <div
      className="border-2 border-dashed border-surface-border rounded-xl p-8 text-center cursor-pointer hover:border-accent transition-colors"
      onClick={() => inputRef.current?.click()}
      onDragOver={(e) => e.preventDefault()}
      onDrop={(e) => {
        e.preventDefault();
        const file = e.dataTransfer.files[0];
        if (file) handleFile(file);
      }}
    >
      <input
        ref={inputRef}
        type="file"
        accept=".pdf,.txt,.md"
        className="hidden"
        onChange={(e) => {
          const file = e.target.files?.[0];
          if (file) handleFile(file);
        }}
      />
      {uploading ? (
        <p className="text-accent">Processing document...</p>
      ) : (
        <>
          <p className="text-lg font-medium mb-1">Drop a document here</p>
          <p className="text-sm text-gray-400">PDF, TXT, or Markdown</p>
        </>
      )}
      {error && <p className="text-red-400 text-sm mt-2">{error}</p>}
    </div>
  );
}
