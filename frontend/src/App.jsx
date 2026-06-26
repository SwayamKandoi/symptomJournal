import { BrowserRouter, Navigate, Outlet, Route, Routes } from 'react-router-dom'
import Navbar from './components/Navbar'
import Dashboard from './pages/Dashboard'
import Insights from './pages/Insights'
import Landing from './pages/Landing'
import Login from './pages/Login'
import LogSymptom from './pages/LogSymptom'
import Register from './pages/Register'

const isLoggedIn = () => !!localStorage.getItem('token')

function AuthLayout() {
  if (!isLoggedIn()) return <Navigate to="/" replace />
  return (
    <div className="min-h-screen flex flex-col">
      <Navbar />
      <main className="flex-1 max-w-4xl mx-auto w-full px-4 py-8">
        <Outlet />
      </main>
    </div>
  )
}

export default function App() {
  const loggedIn = isLoggedIn()
  return (
    <BrowserRouter>
      <Routes>
        {/* Public */}
        <Route path="/" element={loggedIn ? <Navigate to="/dashboard" replace /> : <Landing />} />
        <Route path="/login" element={loggedIn ? <Navigate to="/dashboard" replace /> : <Login />} />
        <Route path="/register" element={loggedIn ? <Navigate to="/dashboard" replace /> : <Register />} />

        {/* Protected — shares Navbar layout via Outlet */}
        <Route element={<AuthLayout />}>
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/log" element={<LogSymptom />} />
          <Route path="/insights" element={<Insights />} />
        </Route>
      </Routes>
    </BrowserRouter>
  )
}
