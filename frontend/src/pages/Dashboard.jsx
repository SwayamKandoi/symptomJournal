import { useEffect, useState } from 'react'
import api from '../api'
import InsightCard from '../components/InsightCard'
import LogCard from '../components/LogCard'
import SymptomChart from '../components/SymptomChart'

export default function Dashboard() {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [generating, setGenerating] = useState(false)

  async function fetchDashboard() {
    const { data } = await api.get('/dashboard')
    setData(data)
  }

  useEffect(() => {
    fetchDashboard().finally(() => setLoading(false))
  }, [])

  async function generateDailyInsight() {
    setGenerating(true)
    try {
      await api.post('/insights/daily')
      await fetchDashboard()
    } finally {
      setGenerating(false)
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64 text-slate-400">
        Loading…
      </div>
    )
  }

  return (
    <div className="space-y-8">
      {/* Stats row */}
      <div className="grid grid-cols-3 gap-4">
        <StatCard label="Total logs" value={data.total_logs} />
        <StatCard
          label="Top symptom"
          value={data.symptom_frequencies[0]?.name ?? '—'}
        />
        <StatCard
          label="Unique symptoms"
          value={data.symptom_frequencies.length}
        />
      </div>

      {/* Chart */}
      <section className="bg-white rounded-2xl border border-slate-200 shadow-sm p-5">
        <h2 className="text-sm font-semibold text-slate-700 mb-4">
          Symptom frequency (last 30 days)
        </h2>
        <SymptomChart data={data.symptom_frequencies} />
      </section>

      {/* Today's insight */}
      <section className="space-y-3">
        <div className="flex items-center justify-between">
          <h2 className="text-sm font-semibold text-slate-700">Daily insight</h2>
          <button
            onClick={generateDailyInsight}
            disabled={generating}
            className="text-xs text-brand-600 bg-brand-50 hover:bg-brand-100 px-3 py-1 rounded-full transition-colors disabled:opacity-50"
          >
            {generating ? 'Generating…' : 'Generate for today'}
          </button>
        </div>
        {data.latest_insight ? (
          <InsightCard insight={data.latest_insight} />
        ) : (
          <p className="text-sm text-slate-400">
            No insight yet — log some symptoms and hit "Generate for today".
          </p>
        )}
      </section>

      {/* Recent logs */}
      <section className="space-y-3">
        <h2 className="text-sm font-semibold text-slate-700">Recent logs</h2>
        {data.recent_logs.length === 0 ? (
          <p className="text-sm text-slate-400">No logs yet.</p>
        ) : (
          data.recent_logs.map((log) => <LogCard key={log.id} log={log} />)
        )}
      </section>
    </div>
  )
}

function StatCard({ label, value }) {
  return (
    <div className="bg-white rounded-2xl border border-slate-200 shadow-sm p-4 text-center">
      <p className="text-2xl font-bold text-brand-600">{value}</p>
      <p className="text-xs text-slate-500 mt-0.5">{label}</p>
    </div>
  )
}
