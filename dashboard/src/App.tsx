import { BrowserRouter as Router, Routes, Route, Link, Navigate, useLocation } from "react-router-dom"
import { useAuth, AuthProvider } from "./contexts/AuthContext"

import SignIn from "./pages/SignIn"
import SignUp from "./pages/SignUp"
import TrackingDashboard from "./pages/TrackingDashboard"
import EventsPage from "./pages/EventsPage"
import AnalyticsPage from "./pages/AnalyticsPage"
import HighlightsPage from "./pages/HighlightsPage"
import VideoUploadPage from "./pages/VideoUploadPage"

function Sidebar() {
  const location = useLocation()

  const navItems = [
    { name: "Live Tracking", path: "/", icon: "📍" },
    { name: "Upload Video", path: "/upload", icon: "🎬" },
    { name: "Events", path: "/events", icon: "⚡" },
    { name: "Highlights", path: "/highlights", icon: "⭐" },
    { name: "Analytics", path: "/analytics", icon: "📊" },
  ]

  return (
    <div className="glass-panel w-64 flex-shrink-0 flex flex-col h-full sticky top-0 z-50">
      <div className="h-16 flex items-center px-6 border-b border-slate-800">
        <Link to="/" className="text-xl font-bold flex items-center gap-2">
          <span className="text-2xl">🏟️</span>
          <span className="bg-clip-text text-transparent bg-gradient-to-r from-primary-400 to-primary-200">
            Sports Analysis
          </span>
        </Link>
      </div>

      <div className="flex-1 overflow-y-auto py-6 px-4 space-y-1">
        {navItems.map((item) => {
          const isActive = location.pathname === item.path
          return (
            <Link
              key={item.path}
              to={item.path}
              className={`flex items-center gap-3 px-4 py-3 rounded-xl transition-all duration-200 group ${isActive
                ? "bg-primary-500/10 text-primary-400 shadow-[inset_0_0_12px_rgba(3,179,179,0.1)]"
                : "text-slate-400 hover:bg-slate-800/50 hover:text-slate-100"
                }`}
            >
              <span className={`text-xl transition-transform duration-300 ${isActive ? 'scale-110' : 'group-hover:scale-110'}`}>
                {item.icon}
              </span>
              <span className={`font-medium ${isActive ? 'glow-text' : ''}`}>
                {item.name}
              </span>
            </Link>
          )
        })}
      </div>

      <div className="p-4 border-t border-slate-800">
        <div className="rounded-xl bg-slate-900/50 p-4 border border-slate-800">
          <p className="text-xs font-medium text-slate-500 uppercase tracking-wider mb-2">System Status</p>
          <div className="flex items-center gap-2 text-sm text-slate-300">
            <span className="flex h-2.5 w-2.5">
              <span className="animate-ping absolute inline-flex h-2.5 w-2.5 rounded-full bg-primary-400 opacity-75"></span>
              <span className="relative inline-flex rounded-full h-2.5 w-2.5 bg-primary-500"></span>
            </span>
            <span>API Online</span>
          </div>
        </div>
      </div>
    </div>
  )
}

function RequireAuth({ children }: { children: JSX.Element }) {
  const { isAuthenticated } = useAuth()
  const location = useLocation()

  if (!isAuthenticated) {
    return <Navigate to="/signin" state={{ from: location }} replace />
  }
  return children
}

function App() {
  return (
    <AuthProvider>
      <Router>
      <div className="flex min-h-screen text-slate-100">
        <Sidebar />

        <main className="flex-1 flex flex-col min-w-0 overflow-hidden relative z-10">
          <div className="flex-1 overflow-y-auto p-8 animate-fade-in">
            <div className="max-w-7xl mx-auto">
              <Routes>
                <Route path="/signin" element={<SignIn />} />
                <Route path="/signup" element={<SignUp />} />
                <Route
                  index
                  element={
                    <RequireAuth>
                      <TrackingDashboard />
                    </RequireAuth>
                  }
                />
                <Route
                  path="/upload"
                  element={
                    <RequireAuth>
                      <VideoUploadPage />
                    </RequireAuth>
                  }
                />
                <Route
                  path="/events"
                  element={
                    <RequireAuth>
                      <EventsPage />
                    </RequireAuth>
                  }
                />
                <Route
                  path="/analytics"
                  element={
                    <RequireAuth>
                      <AnalyticsPage />
                    </RequireAuth>
                  }
                />
                <Route
                  path="/highlights"
                  element={
                    <RequireAuth>
                      <HighlightsPage />
                    </RequireAuth>
                  }
                />
              </Routes>
            </div>
          </div>
        </main>
      </div>
    </Router>
    </AuthProvider>
  )
}

export default App
