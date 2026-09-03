import { useState, useRef, useEffect } from "react"

interface Video {
    id: string
    filename: string
    path: string
    size_bytes: number
    status: string
}

interface JobStatus {
    job_id: string
    status: string
}

export default function VideoUploadPage() {
    const [dragActive, setDragActive] = useState(false)
    const [file, setFile] = useState<File | null>(null)
    const [sport, setSport] = useState("football")
    const [uploading, setUploading] = useState(false)
    const [uploadedVideos, setUploadedVideos] = useState<Video[]>([])
    const [activeJobs, setActiveJobs] = useState<Record<string, JobStatus>>({})
    const fileInputRef = useRef<HTMLInputElement>(null)

    useEffect(() => {
        fetchVideos()
    }, [])

    const fetchVideos = async () => {
        try {
            const res = await fetch("/api/v1/videos/")
            const data = await res.json()
            setUploadedVideos(data)

            // Fetch statuses for videos
            data.forEach(async (v: Video) => {
                try {
                    const statusRes = await fetch(`/api/v1/videos/${v.id}/status`)
                    const statusData = await statusRes.json()
                    if (statusData.jobs && statusData.jobs.length > 0) {
                        setActiveJobs(prev => ({
                            ...prev,
                            [v.id]: statusData.jobs[0]
                        }))
                    }
                } catch (e) {
                    // Ignore individual status fetch errors
                }
            })
        } catch (e) {
            console.error(e)
        }
    }

    const handleDrag = (e: React.DragEvent) => {
        e.preventDefault()
        e.stopPropagation()
        if (e.type === "dragenter" || e.type === "dragover") {
            setDragActive(true)
        } else if (e.type === "dragleave") {
            setDragActive(false)
        }
    }

    const handleDrop = (e: React.DragEvent) => {
        e.preventDefault()
        e.stopPropagation()
        setDragActive(false)
        if (e.dataTransfer.files && e.dataTransfer.files[0]) {
            setFile(e.dataTransfer.files[0])
        }
    }

    const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        e.preventDefault()
        if (e.target.files && e.target.files[0]) {
            setFile(e.target.files[0])
        }
    }

    const onButtonClick = () => {
        fileInputRef.current?.click()
    }

    const handleUpload = async () => {
        if (!file) return
        setUploading(true)
        const formData = new FormData()
        formData.append("file", file)

        try {
            const res = await fetch("/api/v1/videos/upload", {
                method: "POST",
                body: formData,
            })
            if (!res.ok) throw new Error("Upload failed")

            setFile(null)
            await fetchVideos()
        } catch (err) {
            alert("Error uploading video")
        } finally {
            setUploading(false)
        }
    }

    const handleAnalyze = async (videoId: string) => {
        try {
            const res = await fetch(`/api/v1/videos/${videoId}/analyze?sport=${sport}`, {
                method: "POST"
            })
            if (!res.ok) throw new Error("Analysis failed")
            await fetchVideos() // Refresh statuses
        } catch (err) {
            alert("Error triggering analysis")
        }
    }

    return (
        <div className="space-y-8 animate-fade-in">
            <div>
                <h1 className="text-3xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-white to-slate-400">
                    Upload Match Video
                </h1>
                <p className="mt-2 text-slate-400 text-lg">
                    Upload full match footage to run automated tracking and highlight generation.
                </p>
            </div>

            <div className="glass-card rounded-2xl p-8 max-w-3xl">
                <form
                    className="relative"
                    onDragEnter={handleDrag}
                    onSubmit={(e) => e.preventDefault()}
                >
                    <input
                        ref={fileInputRef}
                        type="file"
                        className="hidden"
                        accept="video/*"
                        onChange={handleChange}
                    />
                    <div
                        className={`border-2 border-dashed rounded-xl p-12 text-center transition-all duration-300 ${dragActive
                                ? "border-primary-400 bg-primary-500/10 shadow-[0_0_30px_rgba(3,179,179,0.15)]"
                                : "border-slate-700 bg-slate-800/50 hover:bg-slate-800 hover:border-slate-600"
                            }`}
                        onDragEnter={handleDrag}
                        onDragLeave={handleDrag}
                        onDragOver={handleDrag}
                        onDrop={handleDrop}
                    >
                        <div className="text-6xl mb-4">🎬</div>
                        {!file ? (
                            <>
                                <p className="text-lg text-slate-300 mb-2">
                                    Drag and drop your video file here
                                </p>
                                <p className="text-sm text-slate-500 mb-6">
                                    Supports MP4, AVI, MKV (Max 2GB)
                                </p>
                                <button
                                    onClick={onButtonClick}
                                    className="bg-slate-800 hover:bg-slate-700 text-white font-medium py-2.5 px-6 rounded-lg transition-colors border border-slate-600 hover:shadow-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2 focus:ring-offset-slate-900"
                                >
                                    Browse Files
                                </button>
                            </>
                        ) : (
                            <div className="flex flex-col items-center">
                                <p className="text-xl font-medium text-primary-300 mb-2">{file.name}</p>
                                <p className="text-sm text-slate-400 mb-6">
                                    {(file.size / (1024 * 1024)).toFixed(2)} MB
                                </p>
                                <div className="flex gap-4">
                                    <button
                                        onClick={() => setFile(null)}
                                        className="bg-transparent hover:bg-slate-800 text-slate-300 font-medium py-2 px-4 rounded-lg transition-colors border border-slate-700"
                                        disabled={uploading}
                                    >
                                        Cancel
                                    </button>
                                    <button
                                        onClick={handleUpload}
                                        disabled={uploading}
                                        className="bg-primary-600 hover:bg-primary-500 text-white font-medium py-2 px-8 rounded-lg transition-all shadow-lg glow-text disabled:opacity-50 disabled:cursor-not-allowed"
                                    >
                                        {uploading ? "Uploading..." : "Upload Video"}
                                    </button>
                                </div>
                            </div>
                        )}
                    </div>
                </form>
            </div>

            {uploadedVideos.length > 0 && (
                <div className="pt-8">
                    <h2 className="text-xl font-semibold mb-6 flex items-center gap-2">
                        <span className="text-primary-400">⚡</span> Video Library
                    </h2>
                    <div className="grid gap-4">
                        {uploadedVideos.map((video) => {
                            const job = activeJobs[video.id]
                            const isAnalyzing = job?.status === "queued" || job?.status === "running"

                            return (
                                <div key={video.id} className="glass-card rounded-xl p-5 flex items-center justify-between group hover:border-slate-600 transition-colors">
                                    <div className="flex items-center gap-4">
                                        <div className="w-12 h-12 rounded-lg bg-slate-800 flex items-center justify-center text-2xl border border-slate-700">
                                            🎥
                                        </div>
                                        <div>
                                            <h3 className="font-medium text-slate-200">{video.filename}</h3>
                                            <p className="text-sm text-slate-500">
                                                ID: {video.id} &bull; {(video.size_bytes / (1024 * 1024)).toFixed(1)} MB
                                            </p>
                                        </div>
                                    </div>

                                    <div className="flex items-center gap-4">
                                        {job ? (
                                            <span className={`px-3 py-1 text-xs font-medium rounded-full ${job.status === "done" ? "bg-green-500/10 text-green-400 border border-green-500/20" :
                                                    job.status === "failed" ? "bg-red-500/10 text-red-400 border border-red-500/20" :
                                                        "bg-primary-500/10 text-primary-400 border border-primary-500/20 animate-pulse"
                                                }`}>
                                                Pipeline {job.status.toUpperCase()}
                                            </span>
                                        ) : (
                                            <div className="flex items-center gap-3">
                                                <select
                                                    value={sport}
                                                    onChange={(e) => setSport(e.target.value)}
                                                    className="bg-slate-900 border border-slate-700 text-slate-300 text-sm rounded-lg focus:ring-primary-500 focus:border-primary-500 block px-3 py-2 outline-none"
                                                >
                                                    <option value="football">⚽ Football</option>
                                                    <option value="rugby">🏉 Rugby</option>
                                                    <option value="basketball">🏀 Basketball</option>
                                                </select>
                                                <button
                                                    onClick={() => handleAnalyze(video.id)}
                                                    disabled={isAnalyzing}
                                                    className="bg-slate-800 hover:bg-slate-700 text-emerald-400 font-medium py-2 px-5 rounded-lg border border-slate-700 transition-colors hover:text-emerald-300 focus:outline-none"
                                                >
                                                    Analyze
                                                </button>
                                            </div>
                                        )}
                                    </div>
                                </div>
                            )
                        })}
                    </div>
                </div>
            )}
        </div>
    )
}
