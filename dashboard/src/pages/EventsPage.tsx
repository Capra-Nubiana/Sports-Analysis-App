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
    goal: "bg-red-100 text-red-800",
    scored_basket: "bg-blue-100 text-blue-800",
    try_scored: "bg-red-100 text-red-800",
    tackle: "bg-orange-100 text-orange-800",
    pass: "bg-green-100 text-green-800",
    three_pointer: "bg-cyan-100 text-cyan-800",
    scrum: "bg-purple-100 text-purple-800",
  }

  if (loading) return <div className="text-center py-12">Loading events...</div>
  if (error) return <div className="text-center py-12 text-red-600">Error: {error}</div>

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-gray-900">Match Events</h1>

      {events.length === 0 ? (
        <div className="text-center py-12 text-gray-500">No events detected yet.</div>
      ) : (
        <>
          <EventTimeline events={events} />

          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Type</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Timestamp</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Confidence</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Players</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200 bg-white">
                {events.map((event, i) => (
                  <tr key={i}>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span
                        className={`inline-flex rounded-full px-2.5 py-0.5 text-xs font-medium ${
                          eventTypeColors[event.event_type] || "bg-gray-100 text-gray-800"
                        }`}
                      >
                        {event.event_type}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {event.timestamp.toFixed(2)}s
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                      {(event.confidence * 100).toFixed(0)}%
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                      {event.players_involved.join(", ") || "—"}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </>
      )}
    </div>
  )
}
