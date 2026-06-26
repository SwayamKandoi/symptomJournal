import { Link } from 'react-router-dom'

const FEATURES = [
  {
    icon: '🗒️',
    title: 'Plain-English Logging',
    desc: 'Just type how you feel. No checkboxes, no forms. AI extracts symptoms, severity, and duration automatically.',
  },
  {
    icon: '📊',
    title: 'Visual Dashboard',
    desc: 'See your most frequent symptoms charted over 30 days so patterns become obvious at a glance.',
  },
  {
    icon: '🤖',
    title: 'AI Health Insights',
    desc: 'Get a daily summary and long-term pattern analysis — written in plain English, not medical jargon.',
  },
]

export default function Landing() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-brand-50 via-white to-slate-100 flex flex-col">

      {/* Nav */}
      <nav className="w-full px-6 py-4 flex items-center justify-between max-w-5xl mx-auto">
        <span className="font-bold text-brand-600 text-xl tracking-tight">SymptomJournal</span>
        <div className="flex items-center gap-3">
          <Link
            to="/login"
            className="text-sm font-medium text-slate-600 hover:text-brand-600 transition-colors"
          >
            Sign in
          </Link>
          <Link
            to="/register"
            className="text-sm font-semibold bg-brand-600 hover:bg-brand-700 text-white px-4 py-2 rounded-lg transition-colors"
          >
            Get started free
          </Link>
        </div>
      </nav>

      {/* Hero */}
      <main className="flex-1 flex flex-col items-center justify-center text-center px-4 py-20">
        <div className="inline-flex items-center gap-2 bg-brand-100 text-brand-700 text-xs font-semibold px-3 py-1 rounded-full mb-6 tracking-wide uppercase">
          AI-powered · Built for you
        </div>

        <h1 className="text-5xl sm:text-6xl font-extrabold text-slate-900 leading-tight max-w-2xl">
          Your health,{' '}
          <span className="text-brand-600">understood.</span>
        </h1>

        <p className="mt-5 text-lg text-slate-500 max-w-xl leading-relaxed">
          Log symptoms in plain English. Let AI extract the details, spot recurring patterns,
          and give you a daily health summary — all in one private journal.
        </p>

        <div className="mt-8 flex flex-col sm:flex-row items-center gap-3">
          <Link
            to="/register"
            className="w-full sm:w-auto bg-brand-600 hover:bg-brand-700 text-white font-semibold px-7 py-3 rounded-xl text-sm shadow-md shadow-brand-200 transition-colors"
          >
            Start journaling — it's free
          </Link>
          <Link
            to="/login"
            className="w-full sm:w-auto border border-slate-300 hover:border-brand-400 text-slate-700 font-semibold px-7 py-3 rounded-xl text-sm transition-colors"
          >
            I already have an account
          </Link>
        </div>

        {/* Demo pill */}
        <div className="mt-12 bg-white border border-slate-200 rounded-2xl shadow-sm px-6 py-4 max-w-lg w-full text-left">
          <p className="text-xs text-slate-400 font-medium mb-2">EXAMPLE LOG</p>
          <p className="text-slate-700 text-sm italic">
            "I've had a throbbing headache since noon, maybe a 7 out of 10. Also feeling pretty tired."
          </p>
          <div className="mt-3 flex flex-wrap gap-2">
            {[
              { label: 'headache', severity: '7/10' },
              { label: 'fatigue', severity: '5/10' },
            ].map((s) => (
              <span
                key={s.label}
                className="text-xs bg-brand-50 text-brand-700 border border-brand-100 rounded-full px-3 py-1"
              >
                {s.label} · {s.severity}
              </span>
            ))}
            <span className="text-xs bg-slate-100 text-slate-500 rounded-full px-3 py-1">
              AI extracted in &lt;1s
            </span>
          </div>
        </div>

        {/* Feature cards */}
        <div className="mt-20 grid sm:grid-cols-3 gap-5 max-w-3xl w-full">
          {FEATURES.map((f) => (
            <div
              key={f.title}
              className="bg-white border border-slate-200 rounded-2xl p-5 text-left shadow-sm hover:shadow-md transition-shadow"
            >
              <div className="text-2xl mb-3">{f.icon}</div>
              <h3 className="font-semibold text-slate-800 text-sm mb-1">{f.title}</h3>
              <p className="text-xs text-slate-500 leading-relaxed">{f.desc}</p>
            </div>
          ))}
        </div>
      </main>

      {/* Footer */}
      <footer className="text-center py-6 text-xs text-slate-400">
        Built for hackathon · {new Date().getFullYear()}
      </footer>
    </div>
  )
}
