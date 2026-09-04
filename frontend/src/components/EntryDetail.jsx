export default function EntryDetail({ entry }) {
  if (!entry) {
    return <p className="muted">Select an entry to see the full text.</p>;
  }

  return (
    <div className="entry-detail">
      <h3>Summary</h3>
      <p>{entry.summary}</p>

      <h3>Tags</h3>
      <div className="tags">
        {entry.tags.map((tag) => (
          <span key={tag} className="tag">
            {tag}
          </span>
        ))}
      </div>

      <h3>Original text</h3>
      <p className="original-text">{entry.text}</p>
    </div>
  );
}
