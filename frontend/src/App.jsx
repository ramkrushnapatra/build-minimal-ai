import { useEffect, useState } from "react";
import { fetchItems } from "./api";
import InboxForm from "./components/InboxForm";
import ItemList from "./components/ItemList";
import QueryPanel from "./components/QueryPanel";

export default function App() {
  const [items, setItems] = useState([]);

  async function refresh() {
    try {
      const data = await fetchItems();
      setItems(data);
    } catch (e) {
      setItems([]);
    }
  }

  useEffect(() => {
    refresh();
    const interval = setInterval(refresh, 3000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="flex h-screen">
      <aside className="w-96 border-r border-gray-800 flex flex-col">
        <div className="p-4 border-b border-gray-800">
          <h1 className="text-lg font-bold">AI Knowledge Inbox</h1>
          <p className="text-xs text-gray-500 mt-1">Save notes and URLs, ask questions</p>
        </div>
        <div className="p-4 border-b border-gray-800">
          <InboxForm onSaved={refresh} />
        </div>
        <div className="p-4 flex-1 overflow-y-auto">
          <h2 className="text-sm font-medium text-gray-400 mb-2">Saved Items</h2>
          <ItemList items={items} />
        </div>
      </aside>

      <main className="flex-1 flex flex-col">
        <QueryPanel />
      </main>
    </div>
  );
}
