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
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-900">Live Tracking</h1>
        <div className="flex items-center gap-3">
          <span
            className={`inline-flex items-center rounded-full px-3 py-1 text-sm font-medium ${
              connected ? "bg-green-100 text-green-800" : "bg-red-100 text-red-800"
            }`}
          >
            <span
              className={`mr-2 h-2 w-2 rounded-full ${
                connected ? "bg-green-500" : "bg-red-500"
              }`}
            />
            {connected ? "Connected" : "Disconnected"}
          </span>
          <button
            onClick={handleSendPing}
            className="rounded-md bg-primary-600 px-4 py-2 text-sm font-medium text-white transition-colors hover:bg-primary-700"
          >
            Send Ping
          </button>
        </div>
      </div>

      <div className="grid gap-6 md:grid-cols-3">
        <div className="rounded-lg border border-gray-200 bg-white p-4">
          <h3 className="text-sm font-medium text-gray-500">Tracked Players</h3>
          <p className="text-3xl font-bold text-gray-900">{players.length}</p>
        </div>
        <div className="rounded-lg border border-gray-200 bg-white p-4">
          <h3 className="text-sm font-medium text-gray-500">Teams</h3>
          <p className="text-3xl font-bold text-gray-900">
            {new Set(players.map((p) => p.teamId)).size}
          </p>
        </div>
        <div className="rounded-lg border border-gray-200 bg-white p-4">
          <h3 className="text-sm font-medium text-gray-500">Connection</h3>
          <p className="text-3xl font-bold text-gray-900">
            {connected ? "Online" : "Offline"}
          </p>
        </div>
      </div>

      <div className="rounded-lg border border-gray-200 bg-white p-6">
        <TrackingCanvas width={800} height={450} players={players} />
      </div>
    </div>
  )
}
