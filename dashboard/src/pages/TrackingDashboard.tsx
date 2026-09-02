import { useEffect, useState } from "react"
import TrackingCanvas from "../components/TrackingCanvas"
import { useWebSocket } from "../hooks/useWebSocket"

export default function TrackingDashboard() {
  const [wsUrl, setWsUrl] = useState("")

  useEffect(() => {
    const protocol = window.location.protocol === "https:" ? "wss" : "ws"
    setWsUrl(`${protocol}://${window.location.host}/ws/tracking`)
  }, [])

  const { players, connected, sendMessage } = useWebSocket(wsUrl)

  const handleSendPing = () => {
    sendMessage("ping")
  }

  return (
    <div className="space-y-8 animate-fade-in">
      <div className="flex flex-col md:flex-row items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-white to-slate-400">
            Live Tracking
          </h1>
          <p className="mt-2 text-slate-400">Real-time object detection and spatial tracking</p>
        </div>
        <div className="flex items-center gap-4">
          <span
            className={`inline-flex items-center rounded-full px-4 py-1.5 text-sm font-medium border shadow-[0_0_10px_rgba(3,179,179,0.2)] ${connected
                ? "bg-primary-500/10 text-primary-300 border-primary-500/30"
                : "bg-rose-500/10 text-rose-300 border-rose-500/30"
              }`}
          >
            <span
              className={`mr-2 h-2.5 w-2.5 rounded-full ${connected ? "bg-primary-400 animate-pulse" : "bg-rose-500"
                }`}
            />
            {connected ? "Connected" : "Disconnected"}
          </span>
          <button
            onClick={handleSendPing}
            className="rounded-lg bg-slate-800 border border-slate-700 px-5 py-2 text-sm font-medium text-slate-300 transition-colors hover:bg-slate-700 hover:text-white focus:outline-none focus:ring-2 focus:ring-primary-500/50"
          >
            Send Ping
          </button>
        </div>
      </div>

      <div className="grid gap-6 md:grid-cols-3">
        <div className="glass-card rounded-2xl p-6">
          <h3 className="text-sm font-medium text-slate-400 mb-2 uppercase tracking-wider">Tracked Players</h3>
          <p className="text-4xl font-bold text-white glow-text">{players.length}</p>
        </div>
        <div className="glass-card rounded-2xl p-6">
          <h3 className="text-sm font-medium text-slate-400 mb-2 uppercase tracking-wider">Active Teams</h3>
          <p className="text-4xl font-bold text-white glow-text">
            {new Set(players.map((p) => p.teamId)).size}
          </p>
        </div>
        <div className="glass-card rounded-2xl p-6 flex flex-col justify-end">
          <h3 className="text-sm font-medium text-slate-400 mb-2 uppercase tracking-wider">API Connection</h3>
          <p className={`text-2xl font-bold ${connected ? "text-primary-400" : "text-slate-500"}`}>
            {connected ? "Online Stream" : "Offline"}
          </p>
        </div>
      </div>

      <div className="glass-card rounded-2xl p-6 overflow-hidden relative group">
        <div className="absolute inset-0 bg-gradient-to-br from-primary-500/5 to-transparent pointer-events-none" />
        <h3 className="text-sm font-medium text-slate-400 mb-6 uppercase tracking-wider">Spatial Visualization</h3>
        <div className="flex justify-center border border-slate-800 rounded-xl overflow-hidden bg-slate-950 p-4">
          <TrackingCanvas width={900} height={500} players={players} />
        </div>
      </div>
    </div>
  )
}
