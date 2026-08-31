import { useEffect, useState } from "react"

interface HeatmapProps {
  grid: number[][]
  title?: string
}

export default function PlayerHeatmap({ grid, title = "Player Heatmap" }: HeatmapProps) {
  const [data, setData] = useState(grid)

  useEffect(() => {
    setData(grid)
  }, [grid])

  const maxVal = data.length > 0 ? Math.max(...data.flat().map((v) => v), 1) : 1

  return (
    <div className="rounded-lg border border-gray-200 bg-white p-4">
      <h3 className="mb-2 text-lg font-semibold">{title}</h3>
      {data.length === 0 ? (
        <p className="text-gray-500">No position data available.</p>
      ) : (
        <div className="overflow-auto">
          <div
            className="grid gap-[1px] bg-gray-200"
            style={{
              gridTemplateColumns: `repeat(${data[0]?.length || 50}, 1fr)`,
            }}
          >
            {data.map((row, i) =>
              row.map((val, j) => {
                const intensity = val > 0 ? val / maxVal : 0
                const color =
                  intensity > 0.6
                    ? `rgba(34, 197, 94, ${intensity})`
                    : intensity > 0.3
                    ? `rgba(250, 204, 92, ${intensity})`
                    : `rgba(148, 163, 184, ${intensity * 0.5})`
                return (
                  <div
                    key={`${i}-${j}`}
                    className="aspect-square"
                    style={{ backgroundColor: color }}
                    title={`${val.toFixed(1)}`}
                  />
                )
              }),
            )}
          </div>
        </div>
      )}
    </div>
  )
}
