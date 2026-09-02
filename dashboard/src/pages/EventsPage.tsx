import { useEffect, useState } from "react"
import EventTimeline from "../components/EventTimeline"
import { Event } from "../types"

export default function EventsPage() {
  const [events, setEvents] = useState<Event[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    fetch("/api/v1/events/")
      .then((res) => res.json())
      .then((data: Event[]) => {
        setEvents(data)
        setLoading(false)
      })
      .catch((err) => {
        setError(err.message)
        setLoading(false)
      })
  }, [])

  const eventTypeColors: Record<string, string> = {
    goal: "bg-rose-500/20 text-rose-300 border-rose-500/30",
    scored_basket: "bg-blue-500/20 text-blue-300 border-blue-500/30",
    try_scored: "bg-rose-500/20 text-rose-300 border-rose-500/30",
    tackle: "bg-amber-500/20 text-amber-300 border-amber-500/30",
    pass: "bg-emerald-500/20 text-emerald-300 border-emerald-500/30",
    three_pointer: "bg-cyan-500/20 text-cyan-300 border-cyan-500/30",
    scrum: "bg-purple-500/20 text-purple-300 border-purple-500/30",
  }

  if (loading) return <div className="text-center py-20 text-slate-400">Loading timeline...</div>
  if (error) return <div className="text-center py-20 text-rose-400">Error: {error}</div>

  return (
    <div className="space-y-8 animate-fade-in">
      <div>
        <h1 className="text-3xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-white to-slate-400">
          Match Events
        </h1>
        <p className="mt-2 text-slate-400 text-lg">
          Chronological timeline of detected activities and scoring events.
        </p>
      </div>

      {events.length === 0 ? (
        <div className="glass-card rounded-2xl p-16 text-center text-slate-400 border-dashed">
          <span className="text-4xl mb-4 block">🔍</span>
          No events detected yet. Upload and analyze a video first.
        </div>
      ) : (
        <>
          <div className="glass-card rounded-2xl p-6 relative">
            <div className="absolute inset-x-0 top-0 h-px bg-gradient-to-r from-transparent via-primary-500/50 to-transparent" />
            <h3 className="text-sm font-medium text-slate-400 mb-6 uppercase tracking-wider">Event Intensity Over Time</h3>
            <EventTimeline events={events} />
          </div>

          <div className="glass-card rounded-2xl overflow-hidden">
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-slate-800/50">
                <thead className="bg-slate-900/50">
                  <tr>
                    <th className="px-6 py-4 text-left text-xs font-semibold text-slate-400 uppercase tracking-wider">Type</th>
                    <th className="px-6 py-4 text-left text-xs font-semibold text-slate-400 uppercase tracking-wider">Timestamp</th>
                    <th className="px-6 py-4 text-left text-xs font-semibold text-slate-400 uppercase tracking-wider">Confidence</th>
                    <th className="px-6 py-4 text-left text-xs font-semibold text-slate-400 uppercase tracking-wider">Players</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800/50 bg-transparent">
                  {events.map((event, i) => (
                    <tr key={i} className="hover:bg-slate-800/30 transition-colors">
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span
                          className={`inline-flex items-center rounded-full px-3 py-1 text-xs font-medium border ${eventTypeColors[event.event_type] || "bg-slate-800 text-slate-300 border-slate-700"
                            }`}
                        >
                          <span className="mr-1.5 h-1.5 w-1.5 rounded-full bg-current opacity-75"></span>
                          {event.event_type.replace('_', ' ').toUpperCase()}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-mono text-slate-300">
                        {event.timestamp.toFixed(2)}s
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="flex items-center gap-2">
                          <span className="text-sm font-medium text-slate-300">{(event.confidence * 100).toFixed(0)}%</span>
                          <div className="w-16 h-1.5 bg-slate-800 rounded-full overflow-hidden">
                            <div
                              className="h-full bg-primary-500 rounded-full"
                              style={{ width: `${event.confidence * 100}%` }}
                            />
                          </div>
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-400">
                        {event.players_involved.length > 0 ? (
                          <div className="flex gap-1">
                            {event.players_involved.map(p => (
                              <span key={p} className="inline-flex h-6 w-6 items-center justify-center rounded-full bg-slate-800 text-xs text-white ring-2 ring-slate-900">
                                {p}
                              </span>
                            ))}
                          </div>
                        ) : "—"}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </>
      )}
    </div>
  )
}
