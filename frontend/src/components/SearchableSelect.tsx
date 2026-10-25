import { useState } from "react";

interface SearchableSelectProps {
  options: { label: string; value: number }[];
  selected: number | null;
  onSelect: (value: number) => void;
  placeholder: string;
}

export function SearchableSelect({ options, selected, onSelect, placeholder }: SearchableSelectProps) {
  const [open, setOpen] = useState(false);
  const [search, setSearch] = useState("");

  const filtered = options.filter(o =>
    o.label.toLowerCase().includes(search.toLowerCase())
  );

  const selectedLabel = options.find(o => o.value === selected)?.label;

  return (
    <div className="relative w-full">
      <button
        onClick={() => setOpen(!open)}
        className="w-full bg-gray-800 text-white rounded-lg px-3 py-2 text-sm text-left flex justify-between items-center"
      >
        {selectedLabel ?? placeholder}
        <span className="text-gray-400">▾</span>
      </button>
      {open && (
        <div className="absolute z-50 w-full mt-1 bg-gray-800 border border-gray-700 rounded-lg shadow-lg">
          <input
            autoFocus
            value={search}
            onChange={e => setSearch(e.target.value)}
            placeholder="Search..."
            className="w-full bg-gray-700 text-white text-sm px-3 py-2 rounded-t-lg outline-none"
          />
          <ul className="max-h-48 overflow-y-auto">
            {filtered.map(o => (
              <li
                key={o.value}
                onClick={() => { onSelect(o.value); setOpen(false); setSearch(""); }}
                className={`px-3 py-2 text-sm cursor-pointer hover:bg-gray-700 ${
                  selected === o.value ? "text-violet-400" : "text-white"
                }`}
              >
                {o.label}
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}