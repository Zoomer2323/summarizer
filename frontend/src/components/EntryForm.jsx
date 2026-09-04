import { useState } from "react";
import { createEntry } from "../api";

export default function EntryForm({ onCreated }) {
  const [text, setText] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  async function handleSubmit(e) {
    e.preventDefault();
    if (!text.trim()) {
      setError("Please enter some text.");
      return;
    }
    setLoading(true);
    setError(null);
    try {
      const entry = await createEntry(text);
      onCreated(entry);
      setText("");
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <form onSubmit={handleSubmit} className="entry-form">
      <textarea
        rows={6}
        placeholder="Paste a note, article draft, or meeting transcript..."
        value={text}
        onChange={(e) => setText(e.target.value)}
        disabled={loading}
      />
      <button type="submit" disabled={loading}>
        {loading ? "Generating summary & tags..." : "Submit"}
      </button>
      {error && <p className="error">{error}</p>}
    </form>
  );
}
