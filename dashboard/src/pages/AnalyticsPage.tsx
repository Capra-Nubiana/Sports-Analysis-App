import { useEffect, useState } from "react"
import DistanceBarChart from "../components/DistanceBarChart"
import PlayerHeatmap from "../components/Heatmap"
import { PlayerReport, DistanceData } from "../types"

// Force Chart.js defaults to dark mode compatible colors
import { Chart, defaults } from 'chart.js'
defaults.color = '#94a3b8' // slate-400
defaults.borderColor = '#1e293b' // slate-800

export default function AnalyticsPage() {
  const [players, setPlayers] = useState<PlayerReport[]>([])
  const [loading, setLoading] = useState(true)
  const [selectedPlayer, setSelectedPlayer] = useState<number | null>(null)

  useEffect(() => {
    fetch("/api/v1/players/")
      .then((res) => res.json())
      .then((data) => {
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

  if (loading) return <div className="text-center py-20 text-slate-400">Loading analytics engine...</div>

  return (
    <div className="space-y-8 animate-fade-in">
      <div>
        <h1 className="text-3xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-white to-slate-400">
          Player Analytics
        </h1>
        <p className="mt-2 text-slate-400 text-lg">
          Metabolic power, distances, and spatial positioning metrics.
        </p>
      </div>

      {players.length === 0 ? (
        <div className="glass-card rounded-2xl p-16 text-center text-slate-400 border-dashed">
          <span className="text-4xl mb-4 block">📊</span>
          No player data available. The dashboard will populate after a video is analyzed.
        </div>
      ) : (
        <>
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4 lg:gap-6">
            {players.map((p) => (
              <div
                key={p.trackId}
                className={`cursor-pointer rounded-2xl p-5 transition-all duration-300 relative group overflow-hidden ${selectedPlayer === p.trackId
                    ? "bg-slate-800/80 border border-primary-500/50 shadow-[0_0_15px_rgba(3,179,179,0.15)]"
                    : "glass-card hover:bg-slate-800/50 hover:border-slate-600"
                  }`}
                onClick={() => setSelectedPlayer(p.trackId)}
              >
                {selectedPlayer === p.trackId && (
                  <div className="absolute top-0 right-0 w-16 h-16 bg-primary-500/20 blur-2xl -mt-8 -mr-8 rounded-full" />
                )}
                <div className="flex justify-between items-start mb-3">
                  <h3 className="font-bold text-white text-lg">Player {p.trackId}</h3>
                  <span className="text-xs font-semibold px-2 py-1 rounded bg-slate-900 border border-slate-700 text-slate-400">
                    Team {p.teamId}
                  </span>
                </div>
                <p className="text-3xl font-bold bg-clip-text text-transparent bg-gradient-to-br from-primary-400 to-primary-600 mb-1">
                  {p.distance.total_distance_m.toFixed(1)}m
                </p>
                <div className="flex items-center gap-3 text-xs text-slate-400 mt-3 pt-3 border-t border-slate-700/50">
                  <span className="flex items-center gap-1"><span className="text-primary-500">⚡</span> {p.sprints.length} sprints</span>
                  <span className="w-1 h-1 rounded-full bg-slate-700"></span>
                  <span>{p.distance.max_speed_ms.toFixed(1)} m/s top</span>
                </div>
              </div>
            ))}
          </div>

          <div className="grid gap-6 xl:grid-cols-2">
            <div className="glass-card rounded-2xl p-6 relative">
              <div className="absolute inset-x-0 top-0 h-px bg-gradient-to-r from-transparent via-primary-500/20 to-transparent" />
              <h3 className="text-sm font-medium text-slate-400 mb-6 uppercase tracking-wider">Distance Covered per Player</h3>
              <div className="h-72 w-full">
                <DistanceBarChart data={distanceData} />
              </div>
            </div>

            {selectedPlayer !== null && (
              <div className="glass-card rounded-2xl p-6 relative">
                <div className="absolute inset-x-0 top-0 h-px bg-gradient-to-r from-transparent via-primary-500/20 to-transparent" />
                <h3 className="text-sm font-medium text-slate-400 mb-6 uppercase tracking-wider">
                  Spatial Heatmap &mdash; Player {selectedPlayer}
                </h3>
                {players.find((p) => p.trackId === selectedPlayer) ? (
                  <div className="h-72 w-full rounded-xl overflow-hidden border border-slate-800 bg-slate-950 flex justify-center p-2">
                    <PlayerHeatmap
                      grid={players.find((p) => p.trackId === selectedPlayer)!.heatmap.grid}
                    />
                  </div>
                ) : (
                  <p className="text-slate-500 text-center py-12">No heatmap data available.</p>
                )}
              </div>
            )}
          </div>
        </>
      )}
    </div>
  )
}
