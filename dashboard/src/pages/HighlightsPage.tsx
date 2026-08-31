import { useEffect, useState } from "react"

interface HighlightClip {
  file: string
  path: string
  reel?: boolean
}

export default function HighlightsPage() {
  const [highlights, setHighlights] = useState<HighlightClip[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    fetch("/api/v1/highlights/")
      .then((res) => res.json())
      .then((data: HighlightClip[]) => {
        setHighlights(data)
        setLoading(false)
      })
      .catch((err) => {
        setError(err.message)
        setLoading(false)
      })
  }, [])

  if (loading) return <div className="text-center py-12">Loading highlights...</div>
  if (error) return <div className="text-center py-12 text-red-600">Error: {error}</div>

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-gray-900">Highlight Clips</h1>

      {highlights.length === 0 ? (
        <div className="text-center py-12 text-gray-500">
          No highlight clips generated. Run analysis with --highlights first.
        </div>
      ) : (
        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
          {highlights.map((clip, i) => (
            <div key={i} className="rounded-lg border border-gray-200 bg-white p-4">
              <div className="flex items-center justify-between">
                <h3 className="font-semibold text-gray-900">{clip.file}</h3>
                {clip.reel && (
                  <span className="inline-flex rounded-full bg-primary-100 px-2.5 py-0.5 text-xs font-medium text-primary-800">
                    Full Reel
                  </span>
                )}
              </div>
              <p className="mt-2 text-sm text-gray-600">Path: {clip.path}</p>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
