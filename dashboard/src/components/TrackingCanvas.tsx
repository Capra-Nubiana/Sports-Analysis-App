import { useEffect, useRef } from "react"

interface Player {
  trackId: number
  teamId: number
  x: number
  y: number
  confidence: number
}

interface TrackingCanvasProps {
  width?: number
  height?: number
  players: Player[]
}

const teamColors: Record<number, string> = {
  0: "#3b82f6",
  1: "#ef4444",
  2: "#f59e42",
}

export default function TrackingCanvas({ width = 800, height = 450, players }: TrackingCanvasProps) {
  const canvasRef = useRef<HTMLCanvasElement | null>(null)

  useEffect(() => {
    const canvas = canvasRef.current
    if (!canvas) return
    const ctx = canvas.getContext("2d")
    if (!ctx) return

    ctx.clearRect(0, 0, width, height)

    // Draw field background
    ctx.fillStyle = "#dcfce8"
    ctx.fillRect(0, 0, width, height)

    // Draw center line
    ctx.strokeStyle = "#16a34a"
    ctx.lineWidth = 2
    ctx.setLineDash([5, 5])
    ctx.beginPath()
    ctx.moveTo(width / 2, 0)
    ctx.lineTo(width / 2, height)
    ctx.stroke()
    ctx.setLineDash([])

    // Draw center circle
    ctx.beginPath()
    ctx.arc(width / 2, height / 2, 40, 0, Math.PI * 2)
    ctx.stroke()

    // Draw goal areas
    ctx.fillStyle = "#fef8f0"
    ctx.fillRect(0, height / 2 - 60, 10, 120)
    ctx.fillRect(width - 10, height / 2 - 60, 10, 120)

    // Draw players
    players.forEach((player) => {
      const color = teamColors[player.teamId] || "#6b7280"
      ctx.fillStyle = color
      ctx.strokeStyle = "#ffffff"
      ctx.lineWidth = 2

      const radius = 8 + (player.confidence * 4)
      ctx.beginPath()
      ctx.arc(player.x, player.y, radius, 0, Math.PI * 2)
      ctx.fill()
      ctx.stroke()

      // Draw track ID
      ctx.fillStyle = "#ffffff"
      ctx.font = "10px monospace"
      ctx.textAlign = "center"
      ctx.fillText(String(player.trackId), player.x, player.y + 3)
    })
  }, [players, width, height])

  return (
    <canvas
      ref={canvasRef}
      width={width}
      height={height}
      className="w-full rounded-lg border-2 border-gray-200 bg-field-200"
    />
  )
}
