export default function InsightCard({ insight }) {
  const date = new Date(insight.generated_at).toLocaleDateString()
  const isPattern = insight.insight_type === 'pattern'

  return (
    <div className={`rounded-xl border p-4 space-y-1 ${isPattern ? 'border-amber-200 bg-amber-50' : 'border-brand-100 bg-brand-50'}`}>
      <div className="flex items-center gap-2">
        <span className={`text-xs font-semibold uppercase tracking-wide ${isPattern ? 'text-amber-600' : 'text-brand-600'}`}>
          {isPattern ? 'Pattern' : 'Daily'}
        </span>
        <span className="text-xs text-slate-400">{date}</span>
      </div>
      <p className="text-sm text-slate-700 leading-relaxed">{insight.content}</p>
    </div>
  )
}
