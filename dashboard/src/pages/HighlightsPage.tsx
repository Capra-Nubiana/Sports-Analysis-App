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

  // Auto-refresh highlights periodically since pipeline runs in background
  useEffect(() => {
    const fetchHighlights = () => {
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
    }

    fetchHighlights()
    const interval = setInterval(fetchHighlights, 5000)
    return () => clearInterval(interval)
  }, [])

  if (loading) return <div className="text-center py-20 text-slate-400">Loading highlights library...</div>
  if (error) return <div className="text-center py-20 text-rose-400">Error: {error}</div>

  const reelClip = highlights.find(h => h.reel)
  const individualClips = highlights.filter(h => !h.reel)

  return (
    <div className="space-y-8 animate-fade-in">
      <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-white to-slate-400">
            Action Highlights
          </h1>
          <p className="mt-2 text-slate-400 text-lg">
            Automatically extracted clips based on high-intensity events.
          </p>
        </div>

        {reelClip && (
          <button className="bg-primary-600 hover:bg-primary-500 text-white font-medium py-2 px-6 rounded-lg transition-all shadow-[0_0_15px_rgba(3,179,179,0.3)] glow-text flex items-center gap-2 border border-primary-400/50">
            <span>🎬</span> Play Full Reel
          </button>
        )}
      </div>

      {highlights.length === 0 ? (
        <div className="glass-card rounded-2xl p-16 text-center text-slate-400 border-dashed">
          <span className="text-4xl mb-4 block">📼</span>
          No highlight clips generated yet. They will appear here once the background pipeline completes analysis and clip extraction.
        </div>
      ) : (
        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
          {reelClip && (
            <div className="lg:col-span-3 glass-card rounded-2xl p-6 border-primary-500/30 shadow-[0_0_20px_rgba(3,179,179,0.1)] group">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-xl font-bold text-white flex items-center gap-2">
                  <span className="text-primary-400">⭐</span> Full Highlight Reel
                </h3>
                <span className="inline-flex rounded-full bg-primary-500/20 px-3 py-1 text-xs font-semibold text-primary-300 border border-primary-500/30 uppercase tracking-widest">
                  Master Cut
                </span>
              </div>
              <div className="aspect-video bg-slate-950 rounded-xl overflow-hidden border border-slate-800 relative group-hover:border-primary-500/50 transition-colors">
                <div className="absolute inset-0 flex items-center justify-center">
                  <span className="text-slate-600">Video Player UI Placeholder for: {reelClip.path}</span>
                </div>
              </div>
            </div>
          )}

          {individualClips.map((clip, i) => (
            <div key={i} className="glass-card rounded-xl overflow-hidden hover:-translate-y-1 hover:shadow-2xl transition-all duration-300 group border-slate-700/50 hover:border-slate-500">
              <div className="aspect-video bg-slate-900 border-b border-slate-700/50 relative">
                <div className="absolute inset-0 flex items-center justify-center group-hover:bg-slate-800 transition-colors cursor-pointer">
                  <div className="w-12 h-12 rounded-full bg-primary-500/20 flex items-center justify-center border border-primary-500/30 group-hover:bg-primary-500/40 group-hover:scale-110 transition-all">
                    <span className="text-primary-300 ml-1">▶</span>
                  </div>
                </div>
              </div>
              <div className="p-5">
                <div className="flex items-center justify-between mb-2">
                  <h3 className="font-semibold text-slate-200 truncate pr-2" title={clip.file}>{clip.file}</h3>
                  <span className="inline-flex rounded-full bg-slate-800 px-2 py-0.5 text-[10px] font-medium text-slate-400 border border-slate-700">
                    MP4
                  </span>
                </div>
                <p className="text-xs text-slate-500 font-mono truncate">{clip.path}</p>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
