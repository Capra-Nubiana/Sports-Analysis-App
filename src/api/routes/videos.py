"""Video upload and analysis REST endpoints."""

import threading
import uuid
from pathlib import Path
from typing import Any

from fastapi import APIRouter, HTTPException, UploadFile

from src.api.app_state import app

router = APIRouter(prefix="/videos", tags=["videos"])

MAX_FILE_SIZE = 2 * 1024 * 1024 * 1024  # 2 GB


def _run_pipeline(job_id: str, video_path: str, sport: str) -> None:
    """Run the analysis pipeline in a background thread."""
    jobs = app.state.store.jobs
    jobs[job_id]["status"] = "running"
    try:
        from src.core.pipeline import Pipeline

        pipeline = Pipeline(
            sport_name=sport,
            video_path=video_path,
            generate_highlights=True,
        )
        pipeline.run()
        jobs[job_id]["status"] = "done"
        jobs[job_id]["timeline"] = f"output/timeline_{Path(video_path).stem}.json"
    except Exception as exc:
        jobs[job_id]["status"] = "failed"
        jobs[job_id]["error"] = str(exc)


@router.post("/upload", response_model=dict[str, Any])
async def upload_video(file: UploadFile) -> dict[str, Any]:
    """Accept a video file via multipart upload."""
    if file.content_type and not file.content_type.startswith("video/"):
        raise HTTPException(status_code=400, detail="Only video files are accepted.")

    original_name = file.filename or "unknown.mp4"
    video_id = uuid.uuid4().hex[:12]
    safe_name = f"{video_id}_{original_name}"

    uploads_dir = app.state.store.uploads_dir
    uploads_dir.mkdir(parents=True, exist_ok=True)

    dest = uploads_dir / safe_name
    total_bytes = 0
    chunk_size = 1024 * 1024  # 1 MB chunks

    with open(dest, "wb") as out:
        while True:
            chunk = await file.read(chunk_size)
            if not chunk:
                break
            total_bytes += len(chunk)
            if total_bytes > MAX_FILE_SIZE:
                out.close()
                dest.unlink(missing_ok=True)
                raise HTTPException(status_code=413, detail="File exceeds 2 GB limit.")
            out.write(chunk)

    # Register in state
    app.state.store.uploaded_videos[video_id] = {
        "id": video_id,
        "filename": original_name,
        "path": str(dest),
        "size_bytes": total_bytes,
        "status": "uploaded",
    }

    return {"id": video_id, "filename": original_name, "size_bytes": total_bytes}


@router.get("/", response_model=list[dict[str, Any]])
async def list_videos() -> list[dict[str, Any]]:
    """List all uploaded videos."""
    return list(app.state.store.uploaded_videos.values())


@router.post("/{video_id}/analyze", response_model=dict[str, Any])
async def analyze_video(video_id: str, sport: str = "football") -> dict[str, Any]:
    """Trigger background pipeline analysis on an uploaded video."""
    videos = app.state.store.uploaded_videos
    if video_id not in videos:
        raise HTTPException(status_code=404, detail=f"Video not found: {video_id}")

    video_info = videos[video_id]
    job_id = uuid.uuid4().hex[:12]

    app.state.store.jobs[job_id] = {
        "job_id": job_id,
        "video_id": video_id,
        "sport": sport,
        "status": "queued",
    }

    thread = threading.Thread(
        target=_run_pipeline,
        args=(job_id, video_info["path"], sport),
        daemon=True,
    )
    thread.start()

    return {"job_id": job_id, "video_id": video_id, "status": "queued"}


@router.get("/{video_id}/status", response_model=dict[str, Any])
async def get_video_status(video_id: str) -> dict[str, Any]:
    """Get the analysis status for a video by checking all jobs."""
    matching_jobs = [j for j in app.state.store.jobs.values() if j.get("video_id") == video_id]
    if not matching_jobs:
        if video_id in app.state.store.uploaded_videos:
            return {"video_id": video_id, "status": "uploaded", "jobs": []}
        raise HTTPException(status_code=404, detail=f"Video not found: {video_id}")
    return {"video_id": video_id, "jobs": matching_jobs}
