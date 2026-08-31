import { Line } from "react-chartjs-2"
import {
  CategoryScale,
  Chart as ChartJS,
  Legend,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  TimeScale,
} from "chart.js"
import "chartjs-adapter-date-fns"

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  TimeScale
)

interface EventTimelineProps {
  events: Array<{
    event_type: string
    timestamp: number
    confidence: number
  }>
}

const eventColors: Record<string, string> = {
  goal: "#ef4444",
  try_scored: "#ef4444",
  scored_basket: "#3b82f6",
  tackle: "#f59e42",
  pass: "#22c55e",
  scrum: "#8b5cf6",
  three_pointer: "#06b6d4",
}

export default function EventTimeline({ events }: EventTimelineProps) {
  const datasets = Object.entries(
    events.reduce(
      (acc, e) => {
        const key = e.event_type
        if (!acc[key]) acc[key] = { data: [], color: eventColors[key] || "#6b7280" }
        acc[key].data.push({ x: e.timestamp, y: e.confidence })
        return acc
      },
      {} as Record<string, { data: Array<{ x: number; y: number }>; color: string }>,
    ),
  ).map(([type, info]) => ({
    label: type,
    data: info.data,
    borderColor: info.color,
    backgroundColor: info.color,
    pointRadius: 6,
    tension: 0.3,
  }))

  const chartData = { datasets }

  const options = {
    responsive: true,
    plugins: {
      legend: { position: "top" as const },
      title: { display: true, text: "Event Timeline" },
    },
    scales: {
      x: { title: { display: true, text: "Time (s)" } },
      y: { title: { display: true, text: "Confidence" }, min: 0, max: 1 },
    },
  }

  return <Line options={options} data={chartData} />
}
