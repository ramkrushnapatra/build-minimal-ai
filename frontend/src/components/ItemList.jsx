const statusStyle = {
  processing: "text-yellow-400",
  indexed: "text-green-400",
  failed: "text-red-400",
};

export default function ItemList({ items }) {
  if (items.length === 0) {
    return <p className="text-gray-500 text-sm">No saved items yet.</p>;
  }

  return (
    <ul className="space-y-2">
      {items.map((item) => (
        <li key={item.id} className="bg-gray-900 border border-gray-800 rounded-lg p-3">
          <div className="flex items-start justify-between gap-2">
            <div className="min-w-0">
              <p className="text-sm font-medium truncate">{item.title}</p>
              <p className="text-xs text-gray-500 mt-0.5">
                {item.source_type} · {new Date(item.created_at).toLocaleString()}
              </p>
            </div>
            <span className={`text-xs shrink-0 ${statusStyle[item.status]}`}>{item.status}</span>
          </div>
          {item.url && (
            <a href={item.url} target="_blank" rel="noreferrer" className="text-xs text-blue-400 truncate block mt-1">
              {item.url}
            </a>
          )}
          <p className="text-xs text-gray-400 mt-2 line-clamp-2">{item.preview}</p>
          {item.error_message && <p className="text-xs text-red-400 mt-1">{item.error_message}</p>}
        </li>
      ))}
    </ul>
  );
}
