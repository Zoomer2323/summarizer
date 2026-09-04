export default function EntryList({ entries, selectedId, onSelect }) {
  if (entries.length === 0) {
    return <p className="muted">No entries yet. Submit some text above to get started.</p>;
  }

  return (
    <ul className="entry-list">
      {entries.map((entry) => (
        <li
          key={entry.id}
          className={entry.id === selectedId ? "selected" : ""}
          onClick={() => onSelect(entry.id)}
        >
          <p className="summary">{entry.summary}</p>
          <div className="tags">
            {entry.tags.map((tag) => (
              <span key={tag} className="tag">
                {tag}
              </span>
            ))}
          </div>
          <span className="timestamp">{new Date(entry.created_at).toLocaleString()}</span>
        </li>
      ))}
    </ul>
  );
}
