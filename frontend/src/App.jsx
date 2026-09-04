import { useEffect, useState } from "react";
import EntryForm from "./components/EntryForm";
import EntryList from "./components/EntryList";
import EntryDetail from "./components/EntryDetail";
import { getEntries } from "./api";
import "./App.css";

export default function App() {
  const [entries, setEntries] = useState([]);
  const [selectedId, setSelectedId] = useState(null);
  const [listError, setListError] = useState(null);

  useEffect(() => {
    getEntries()
      .then(setEntries)
      .catch((err) => setListError(err.message));
  }, []);

  function handleCreated(entry) {
    setEntries((prev) => [entry, ...prev]);
    setSelectedId(entry.id);
  }

  const selectedEntry = entries.find((e) => e.id === selectedId) || null;

  return (
    <div className="app">
      <h1>AI Content Assistant</h1>
      <p className="muted">
        Paste text below. The backend calls Gemini to generate a summary and three tags,
        then saves the result.
      </p>

      <EntryForm onCreated={handleCreated} />

      <div className="columns">
        <div>
          <h2>Saved entries</h2>
          {listError && <p className="error">{listError}</p>}
          <EntryList entries={entries} selectedId={selectedId} onSelect={setSelectedId} />
        </div>
        <div>
          <h2>Detail</h2>
          <EntryDetail entry={selectedEntry} />
        </div>
      </div>
    </div>
  );
}
