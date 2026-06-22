interface WeaknessesListProps {
  weaknesses: string[];
}

export default function WeaknessesList({ weaknesses }: WeaknessesListProps) {
  if (!weaknesses.length) return null;

  return (
    <div className="bg-red-50 rounded-2xl border border-red-100 p-6">
      <h2 className="text-lg font-semibold text-red-800 mb-4">
        ⚠️ Key Weaknesses Identified
      </h2>
      <ul className="flex flex-col gap-2">
        {weaknesses.map((weakness, index) => (
          <li key={index} className="flex gap-3">
            <span className="text-red-400 mt-0.5 flex-shrink-0">✕</span>
            <p className="text-sm text-red-900 leading-relaxed">{weakness}</p>
          </li>
        ))}
      </ul>
    </div>
  );
}