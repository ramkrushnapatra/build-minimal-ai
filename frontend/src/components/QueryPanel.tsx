import { useState } from "react";
import { askQuestion } from "../api";
import type { QueryResult } from "../types";

export default function QueryPanel() {
  const [question, setQuestion] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<QueryResult | null>(null);

  async function handleAsk(e: React.FormEvent) {
    e.preventDefault();
    const q = question.trim();
    if (!q || loading) return;

    setLoading(true);
    setError(null);
    try {
      const data = await askQuestion(q);
      setResult(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Query failed");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="flex flex-col h-full">
      <form onSubmit={handleAsk} className="flex gap-2 p-4 border-b border-gray-800">
        <input
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          placeholder="Ask a question over your saved content..."
          className="flex-1 bg-gray-900 border border-gray-700 rounded-lg px-4 py-2 text-sm focus:outline-none focus:border-blue-500"
        />
        <button
          type="submit"
          disabled={loading || !question.trim()}
          className="bg-blue-600 hover:bg-blue-700 disabled:opacity-50 text-white px-5 py-2 rounded-lg text-sm font-medium"
        >
          {loading ? "..." : "Ask"}
        </button>
      </form>

      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {error && <p className="text-red-400 text-sm">{error}</p>}

        {!result && !error && (
          <p className="text-gray-500 text-sm text-center mt-8">
            Save some notes or URLs, then ask a question.
          </p>
        )}

        {result && (
          <>
            <div className="bg-gray-900 border border-gray-800 rounded-lg p-4">
              <h3 className="text-sm font-medium text-gray-400 mb-2">Answer</h3>
              <p className="text-sm whitespace-pre-wrap">{result.answer}</p>
            </div>

            {result.sources.length > 0 && (
              <div>
                <h3 className="text-sm font-medium text-gray-400 mb-2">Sources</h3>
                <ul className="space-y-2">
                  {result.sources.map((src, i) => (
                    <li key={i} className="bg-gray-900 border border-gray-800 rounded-lg p-3 text-sm">
                      <div className="flex justify-between gap-2">
                        <span className="font-medium text-blue-400 truncate">{src.title}</span>
                        <span className="text-xs text-gray-500 shrink-0">{(src.score * 100).toFixed(0)}%</span>
                      </div>
                      <p className="text-xs text-gray-400 mt-1">{src.snippet}</p>
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
}
