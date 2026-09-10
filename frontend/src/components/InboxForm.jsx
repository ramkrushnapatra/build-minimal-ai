import { useState } from "react";
import { ingestNote, ingestUrl } from "../api";

export default function InboxForm({ onSaved }) {
  const [mode, setMode] = useState("note");
  const [noteText, setNoteText] = useState("");
  const [urlText, setUrlText] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function handleSubmit(e) {
    e.preventDefault();
    setLoading(true);
    setError("");
    try {
      if (mode === "note") {
        await ingestNote(noteText.trim());
        setNoteText("");
      } else {
        await ingestUrl(urlText.trim());
        setUrlText("");
      }
      onSaved();
    } catch (err) {
      setError(err.message || "Save failed");
    } finally {
      setLoading(false);
    }
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-3">
      <div className="flex gap-2">
        <button
          type="button"
          onClick={() => setMode("note")}
          className={`px-3 py-1 rounded text-sm ${mode === "note" ? "bg-blue-600 text-white" : "bg-gray-800 text-gray-400"}`}
        >
          Note
        </button>
        <button
          type="button"
          onClick={() => setMode("url")}
          className={`px-3 py-1 rounded text-sm ${mode === "url" ? "bg-blue-600 text-white" : "bg-gray-800 text-gray-400"}`}
        >
          URL
        </button>
      </div>

      {mode === "note" ? (
        <textarea
          value={noteText}
          onChange={(e) => setNoteText(e.target.value)}
          placeholder="Write a note..."
          rows={4}
          className="w-full bg-gray-900 border border-gray-700 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-blue-500"
        />
      ) : (
        <input
          type="url"
          value={urlText}
          onChange={(e) => setUrlText(e.target.value)}
          placeholder="https://example.com/article"
          className="w-full bg-gray-900 border border-gray-700 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-blue-500"
        />
      )}

      <button
        type="submit"
        disabled={loading || (mode === "note" ? !noteText.trim() : !urlText.trim())}
        className="w-full bg-blue-600 hover:bg-blue-700 disabled:opacity-50 text-white py-2 rounded-lg text-sm font-medium"
      >
        {loading ? "Saving..." : "Save"}
      </button>

      {error && <p className="text-red-400 text-sm">{error}</p>}
    </form>
  );
}
