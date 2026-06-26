import { useEffect, useState } from 'react'
import api from '../api'
import InsightCard from '../components/InsightCard'

export default function Insights() {
  const [insights, setInsights] = useState([])
  const [loading, setLoading] = useState(true)
  const [generating, setGenerating] = useState(null) // 'daily' | 'pattern' | null

  async function fetchInsights() {
    const { data } = await api.get('/insights')
    setInsights(data)
  }

  useEffect(() => {
    fetchInsights().finally(() => setLoading(false))
  }, [])

  async function generate(type) {
    setGenerating(type)
    try {
      await api.post(`/insights/${type}`)
      await fetchInsights()
    } finally {
      setGenerating(null)
    }
  }

  return (
    <div className="space-y-6 max-w-2xl mx-auto">
      <div>
        <h1 className="text-xl font-bold text-slate-800">AI Insights</h1>
        <p className="text-sm text-slate-500 mt-0.5">
          Generate a daily summary or let AI scan for recurring patterns.
        </p>
      </div>

      <div className="flex gap-3">
        <button
          onClick={() => generate('daily')}
          disabled={!!generating}
          className="flex-1 bg-brand-600 hover:bg-brand-700 text-white text-sm font-semibold py-2.5 rounded-xl transition-colors disabled:opacity-50"
        >
          {generating === 'daily' ? 'Generating…' : 'Daily insight'}
        </button>
        <button
          onClick={() => generate('pattern')}
          disabled={!!generating}
          className="flex-1 bg-amber-500 hover:bg-amber-600 text-white text-sm font-semibold py-2.5 rounded-xl transition-colors disabled:opacity-50"
        >
          {generating === 'pattern' ? 'Analysing…' : 'Pattern analysis'}
        </button>
      </div>

      {loading ? (
        <p className="text-sm text-slate-400">Loading…</p>
      ) : insights.length === 0 ? (
        <p className="text-sm text-slate-400">
          No insights yet. Generate one above after logging some symptoms.
        </p>
      ) : (
        <div className="space-y-3">
          {insights.map((insight) => (
            <InsightCard key={insight.id} insight={insight} />
          ))}
        </div>
      )}
    </div>
  )
}
