export default function LogCard({ log }) {
  const date = new Date(log.logged_at).toLocaleString()

  return (
    <div className="bg-white rounded-xl border border-slate-200 p-4 space-y-2">
      <div className="flex items-center justify-between">
        <span className="text-xs text-slate-400">{date}</span>
        {log.overall_severity != null && (
          <span className="text-xs font-semibold px-2 py-0.5 rounded-full bg-brand-100 text-brand-700">
            severity {log.overall_severity.toFixed(1)}
          </span>
        )}
      </div>
      <p className="text-sm text-slate-700 italic">"{log.raw_text}"</p>
      {log.symptoms.length > 0 && (
        <div className="flex flex-wrap gap-1.5 pt-1">
          {log.symptoms.map((s, i) => (
            <span
              key={i}
              className="text-xs bg-slate-100 text-slate-600 rounded-full px-2.5 py-0.5"
            >
              {s.name}
              {s.severity != null ? ` · ${s.severity}/10` : ''}
            </span>
          ))}
        </div>
      )}
    </div>
  )
}
