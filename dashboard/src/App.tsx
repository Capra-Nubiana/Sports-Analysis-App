import { useEffect, useState } from "react"
import { BrowserRouter as Router, Routes, Route, Link, NavLink } from "react-router-dom"

import TrackingDashboard from "./pages/TrackingDashboard"
import EventsPage from "./pages/EventsPage"
import AnalyticsPage from "./pages/AnalyticsPage"
import HighlightsPage from "./pages/HighlightsPage"

function App() {
  return (
    <Router>
      <div className="min-h-screen bg-gray-50">
        <nav className="bg-white shadow">
          <div className="container mx-auto px-4">
            <div className="flex h-16 items-center justify-between">
              <div className="flex items-center space-x-4">
                <Link to="/" className="text-xl font-bold text-primary-700">
                  Sports Analysis
                </Link>
                <NavLink
                  to="/"
                  className={({ isActive }) =>
                    `px-3 py-2 rounded-md text-sm font-medium ${
                      isActive
                        ? "bg-primary-100 text-primary-700"
                        : "text-gray-600 hover:text-gray-900 hover:bg-gray-100"
                    }`
                  }
                >
                  Live Tracking
                </NavLink>
                <NavLink
                  to="/events"
                  className={({ isActive }) =>
                    `px-3 py-2 rounded-md text-sm font-medium ${
                      isActive
                        ? "bg-primary-100 text-primary-700"
                        : "text-gray-600 hover:text-gray-900 hover:bg-gray-100"
                    }`
                  }
                >
                  Events
                </NavLink>
                <NavLink
                  to="/analytics"
                  className={({ isActive }) =>
                    `px-3 py-2 rounded-md text-sm font-medium ${
                      isActive
                        ? "bg-primary-100 text-primary-700"
                        : "text-gray-600 hover:text-gray-900 hover:bg-gray-100"
                    }`
                  }
                >
                  Analytics
                </NavLink>
                <NavLink
                  to="/highlights"
                  className={({ isActive }) =>
                    `px-3 py-2 rounded-md text-sm font-medium ${
                      isActive
                        ? "bg-primary-100 text-primary-700"
                        : "text-gray-600 hover:text-gray-900 hover:bg-gray-100"
                    }`
                  }
                >
                  Highlights
                </NavLink>
              </div>
            </div>
          </div>
        </nav>

        <main className="container mx-auto px-4 py-6">
          <Routes>
            <Route index element={<TrackingDashboard />} />
            <Route path="/events" element={<EventsPage />} />
            <Route path="/analytics" element={<AnalyticsPage />} />
            <Route path="/highlights" element={<HighlightsPage />} />
          </Routes>
        </main>
      </div>
    </Router>
  )
}

export default App
