import { Bar } from "react-chartjs-2"
import {
  CategoryScale,
  Chart as ChartJS,
  Legend,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
} from "chart.js"

ChartJS.register(CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend)

interface DistanceBarChartProps {
  data: Array<{ trackId: number; distance: number; highSpeed: number }>
}

export default function DistanceBarChart({ data }: DistanceBarChartProps) {
  const chartData = {
    labels: data.map((d) => `P${d.trackId}`),
    datasets: [
      {
        label: "Total Distance (m)",
        data: data.map((d) => d.distance),
        backgroundColor: "rgba(34, 197, 94, 0.7)",
      },
      {
        label: "High-Speed Distance (m)",
        data: data.map((d) => d.highSpeed),
        backgroundColor: "rgba(239, 68, 68, 0.7)",
      },
    ],
  }

  const options = {
    responsive: true,
    plugins: {
      legend: { position: "top" as const },
      title: { display: true, text: "Distance Covered" },
    },
    scales: {
      y: { beginAtZero: true },
    },
  }

  return <Bar options={options} data={chartData} />
}
