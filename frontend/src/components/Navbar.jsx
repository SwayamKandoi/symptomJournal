import { Link, useNavigate } from 'react-router-dom'

export default function Navbar() {
  const navigate = useNavigate()

  function logout() {
    localStorage.removeItem('token')
    navigate('/login')
  }

  return (
    <nav className="bg-white border-b border-slate-200 shadow-sm">
      <div className="max-w-4xl mx-auto px-4 h-14 flex items-center justify-between">
        <Link to="/" className="font-semibold text-brand-600 text-lg tracking-tight">
          SymptomJournal
        </Link>
        <div className="flex items-center gap-6 text-sm font-medium text-slate-600">
          <Link to="/dashboard" className="hover:text-brand-600 transition-colors">Dashboard</Link>
          <Link to="/log" className="hover:text-brand-600 transition-colors">Log</Link>
          <Link to="/insights" className="hover:text-brand-600 transition-colors">Insights</Link>
          <button
            onClick={logout}
            className="text-slate-400 hover:text-red-500 transition-colors"
          >
            Sign out
          </button>
        </div>
      </div>
    </nav>
  )
}
