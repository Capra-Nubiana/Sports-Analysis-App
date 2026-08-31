import { useEffect, useRef, useState } from "react"

interface Player {
  trackId: number
  teamId: number
  x: number
  y: number
  confidence: number
}

export function useWebSocket(url: string) {
  const [players, setPlayers] = useState<Player[]>([])
  const [connected, setConnected] = useState(false)
  const wsRef = useRef<WebSocket | null>(null)

  useEffect(() => {
    const ws = new WebSocket(url)
    wsRef.current = ws

    ws.onopen = () => setConnected(true)
    ws.onclose = () => setConnected(false)

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data)
        if (data.players) {
          setPlayers(data.players)
        }
      } catch {
        // Non-JSON message (e.g., echo), ignore
      }
    }

    return () => {
      ws.close()
    }
  }, [url])

  const sendMessage = (message: string) => {
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(message)
    }
  }

  return { players, connected, sendMessage }
}
