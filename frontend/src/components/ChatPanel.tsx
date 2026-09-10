"use client";

import { useRef, useState } from "react";
import type { ChatMessage, Citation } from "@/types";
import { streamChat } from "@/lib/api";

interface Props {
  selectedDocumentIds: string[];
}

export default function ChatPanel({ selectedDocumentIds }: Props) {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState("");
  const [streaming, setStreaming] = useState(false);
  const bottomRef = useRef<HTMLDivElement>(null);

  async function handleSend() {
    const text = input.trim();
    if (!text || streaming) return;

    setInput("");
    setMessages((prev) => [...prev, { role: "user", content: text }]);
    setStreaming(true);

    let assistantText = "";
    let citations: Citation[] = [];

    setMessages((prev) => [...prev, { role: "assistant", content: "" }]);

    await streamChat(
      text,
      selectedDocumentIds.length > 0 ? selectedDocumentIds : null,
      (token) => {
        assistantText += token;
        setMessages((prev) => {
          const updated = [...prev];
          updated[updated.length - 1] = { role: "assistant", content: assistantText, citations };
          return updated;
        });
      },
      (cites) => {
        citations = cites;
      },
      () => setStreaming(false),
      (err) => {
        setMessages((prev) => {
          const updated = [...prev];
          updated[updated.length - 1] = { role: "assistant", content: `Error: ${err}` };
          return updated;
        });
        setStreaming(false);
      },
    );

    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }

  return (
    <div className="flex flex-col h-full">
      <div className="flex-1 overflow-y-auto space-y-4 p-4">
        {messages.length === 0 && (
          <p className="text-gray-500 text-center mt-8">
            Ask a question about your uploaded documents.
          </p>
        )}
        {messages.map((msg, i) => (
          <div key={i} className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}>
            <div
              className={`max-w-[80%] rounded-xl px-4 py-3 text-sm ${
                msg.role === "user"
                  ? "bg-accent text-white"
                  : "bg-surface-card border border-surface-border"
              }`}
            >
              <p className="whitespace-pre-wrap">{msg.content}</p>
              {msg.citations && msg.citations.length > 0 && (
                <div className="mt-3 pt-3 border-t border-surface-border space-y-2">
                  <p className="text-xs text-gray-400 font-medium">Sources</p>
                  {msg.citations.map((c, j) => (
                    <div key={j} className="text-xs text-gray-400 bg-surface rounded p-2">
                      <span className="text-accent">{c.filename}</span>
                      <span className="ml-2 opacity-60">({(c.score * 100).toFixed(0)}%)</span>
                      <p className="mt-1 line-clamp-2">{c.chunk_text}</p>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        ))}
        <div ref={bottomRef} />
      </div>

      <div className="border-t border-surface-border p-4 flex gap-2">
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && !e.shiftKey && handleSend()}
          placeholder="Ask a question..."
          disabled={streaming}
          className="flex-1 bg-surface-card border border-surface-border rounded-lg px-4 py-2 text-sm focus:outline-none focus:border-accent"
        />
        <button
          onClick={handleSend}
          disabled={streaming || !input.trim()}
          className="bg-accent hover:bg-accent-hover disabled:opacity-50 text-white px-5 py-2 rounded-lg text-sm font-medium transition-colors"
        >
          Send
        </button>
      </div>
    </div>
  );
}
