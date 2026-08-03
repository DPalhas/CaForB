export default function ResultsSkeleton() {
  return (
    <div className="w-full max-w-2xl mx-auto animate-pulse">
      {/* Header skeleton */}
      <div className="mb-8 text-center">
        <div className="h-7 bg-slate-800 rounded w-64 mx-auto mb-2" />
        <div className="h-4 bg-slate-800/60 rounded w-48 mx-auto" />
      </div>

      {/* Score card skeleton */}
      <div className="bg-slate-900/60 rounded-2xl p-6 mb-6 border border-slate-800/60">
        <div className="h-4 bg-slate-800 rounded w-40 mb-3" />
        <div className="h-14 bg-slate-800 rounded w-32 mb-4" />
        <div className="h-3 bg-slate-800 rounded w-full" />
      </div>

      {/* Opportunities skeleton */}
      <div className="mb-6">
        <div className="h-5 bg-slate-800 rounded w-48 mb-4" />
        {[1, 2, 3].map((i) => (
          <div key={i} className="bg-slate-900/60 rounded-xl p-5 mb-3 border border-slate-800/60">
            <div className="h-4 bg-slate-800 rounded w-3/4 mb-3" />
            <div className="h-3 bg-slate-800/60 rounded w-full mb-2" />
            <div className="h-3 bg-slate-800/60 rounded w-5/6" />
          </div>
        ))}
      </div>

      {/* Next steps skeleton */}
      <div className="bg-slate-900/60 rounded-2xl p-6 mb-4 border border-slate-800/60">
        <div className="h-5 bg-slate-800 rounded w-48 mb-4" />
        {[1, 2, 3].map((i) => (
          <div key={i} className="h-3 bg-slate-800 rounded w-full mb-3" />
        ))}
      </div>
    </div>
  );
}
