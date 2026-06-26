import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import api from '../api'
import LogCard from '../components/LogCard'

const EXAMPLES = [
  'I have a splitting headache and feel exhausted',
  'My throat is sore and I have a mild fever since morning',
  'Lower back pain, around 6/10, been going on for 3 days',
]

export default function LogSymptom() {
  const navigate = useNavigate()
  const [text, setText] = useState('')
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  async function handleSubmit(e) {
    e.preventDefault()
    if (!text.trim()) return
    setError('')
    setLoading(true)
    setResult(null)
    try {
      const { data } = await api.post('/logs', { raw_text: text })
      setResult(data)
      setText('')
    } catch (err) {
      const detail = err.response?.data?.detail
      setError(typeof detail === 'string' ? detail : JSON.stringify(detail) || err.message || 'Failed to log symptom.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="space-y-6 max-w-2xl mx-auto">
      <div>
        <h1 className="text-xl font-bold text-slate-800">Log Symptoms</h1>
        <p className="text-sm text-slate-500 mt-0.5">
          Describe how you feel in plain English — AI will extract the details.
        </p>
      </div>

      <form onSubmit={handleSubmit} className="bg-white rounded-2xl border border-slate-200 shadow-sm p-5 space-y-4">
        <textarea
          value={text}
          onChange={(e) => setText(e.target.value)}
          rows={4}
          placeholder="e.g. I have a headache and feel tired after lunch…"
          className="w-full border border-slate-300 rounded-xl px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-brand-500 resize-none"
        />
        {error && <p className="text-sm text-red-500">{error}</p>}
        <div className="flex items-center justify-between">
          <div className="flex flex-wrap gap-2">
            {EXAMPLES.map((ex) => (
              <button
                key={ex}
                type="button"
                onClick={() => setText(ex)}
                className="text-xs text-brand-600 bg-brand-50 hover:bg-brand-100 rounded-full px-3 py-1 transition-colors"
              >
                {ex.slice(0, 30)}…
              </button>
            ))}
          </div>
          <button
            type="submit"
            disabled={loading || !text.trim()}
            className="ml-4 shrink-0 bg-brand-600 hover:bg-brand-700 text-white font-semibold px-5 py-2 rounded-xl text-sm transition-colors disabled:opacity-50"
          >
            {loading ? 'Analysing…' : 'Log'}
          </button>
        </div>
      </form>

      {result && (
        <div className="space-y-3">
          <p className="text-sm font-medium text-slate-600">Saved — AI extracted:</p>
          <LogCard log={result} />
          <button
            onClick={() => navigate('/dashboard')}
            className="text-sm text-brand-600 hover:underline"
          >
            View dashboard →
          </button>
        </div>
      )}
    </div>
  )
}
