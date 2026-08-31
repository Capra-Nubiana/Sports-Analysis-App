import { useEffect, useState } from "react"
import DistanceBarChart from "../components/DistanceBarChart"
import PlayerHeatmap from "../components/Heatmap"
import { PlayerReport, DistanceData } from "../types"

export default function AnalyticsPage() {
  const [players, setPlayers] = useState<PlayerReport[]>([])
  const [loading, setLoading] = useState(true)
  const [selectedPlayer, setSelectedPlayer] = useState<number | null>(null)

  useEffect(() => {
    fetch("/api/v1/players/")
      .then((res) => res.json())
      .then((data) => {
        // Build player reports
        const reports: PlayerReport[] = data.map((p: any) => ({
          trackId: p.track_id,
          teamId: p.team_id,
          heatmap: { grid: [], total_points: 0, max_density: 0 },
          distance: { total_distance_m: 0, high_speed_distance_m: 0, average_speed_ms: 0, max_speed_ms: 0 },
          sprints: [],
        }))
        setPlayers(reports)
        if (reports.length > 0) setSelectedPlayer(reports[0].trackId)
        setLoading(false)
      })
      .catch(() => setLoading(false))
  }, [])

  const distanceData: DistanceData[] = players.map((p) => ({
    trackId: p.trackId,
    distance: p.distance.total_distance_m,
    highSpeed: p.distance.high_speed_distance_m,
  }))

  if (loading) return <div className="text-center py-12">Loading analytics...</div>

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-gray-900">Player Analytics</h1>

      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
        {players.map((p) => (
          <div
            key={p.trackId}
            className={`cursor-pointer rounded-lg border p-4 transition-shadow ${
              selectedPlayer === p.trackId
                ? "border-primary-500 shadow-lg ring-2 ring-primary-200"
                : "border-gray-200 hover:shadow-md"
            }`}
            onClick={() => setSelectedPlayer(p.trackId)}
          >
            <h3 className="font-semibold text-gray-900">Player {p.trackId}</h3>
            <p className="text-sm text-gray-600">Team {p.teamId}</p>
            <p className="mt-2 text-2xl font-bold text-primary-600">
              {p.distance.total_distance_m.toFixed(1)}m
            </p>
            <p className="text-xs text-gray-500">
              {p.sprints.length} sprints · {p.distance.max_speed_ms.toFixed(1)} m/s max
            </p>
          </div>
        ))}
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <div className="rounded-lg border border-gray-200 bg-white p-6">
          <h3 className="mb-4 text-lg font-semibold">Distance Covered</h3>
          <DistanceBarChart data={distanceData} />
        </div>

        {selectedPlayer !== null && (
          <div className="rounded-lg border border-gray-200 bg-white p-6">
            <h3 className="mb-4 text-lg font-semibold">Position Heatmap</h3>
            {players.find((p) => p.trackId === selectedPlayer) ? (
              <PlayerHeatmap
                grid={players.find((p) => p.trackId === selectedPlayer)!.heatmap.grid}
              />
            ) : (
              <p className="text-gray-500">No heatmap data available.</p>
            )}
          </div>
        )}
      </div>
    </div>
  )
}
