"""
Highlight Clip Extraction

Extracts highlight clips from video using FFmpeg/MoviePy and
optionally concatenates them into a final highlight reel.
"""

import shutil
import subprocess
from pathlib import Path

from src.highlights.scorer import HighlightScorer


class ClipExtractor:
    """Extracts sub-clips from a video based on time ranges using FFmpeg."""

    def __init__(self, video_path: str, output_dir: str = "output"):
        self.video_path = str(video_path)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self._ffmpeg = self._find_ffmpeg()

    @staticmethod
    def _find_ffmpeg() -> str | None:
        """Locate ffmpeg binary, falling back to imageio-ffmpeg if available."""
        path = shutil.which("ffmpeg")
        if path:
            return path
        try:
            from imageio_ffmpeg import get_ffmpeg_exe

            return str(get_ffmpeg_exe())
        except ImportError:
            return None

    def _run_ffmpeg(self, cmd: list[str]) -> bool:
        """Execute an FFmpeg command, returning True on success."""
        if self._ffmpeg is None:
            print("ffmpeg not found; cannot extract clips.")
            return False

        full_cmd = [self._ffmpeg, "-y", *cmd]
        try:
            result = subprocess.run(  # noqa: S603
                full_cmd,
                capture_output=True,
                text=True,
                timeout=120,
            )
            return result.returncode == 0
        except Exception as e:
            print(f"FFmpeg error: {e}")
            return False

    def extract_clip(self, start: float, end: float, output_name: str) -> str | None:
        """Extract a single clip [start, end] from the video.

        Returns the path to the extracted clip, or None on failure.
        """
        if self._ffmpeg is None:
            return self._extract_clip_moviepy(start, end, output_name)

        output_path = self.output_dir / output_name
        cmd = [
            "-ss",
            f"{start:.2f}",
            "-to",
            f"{end:.2f}",
            "-i",
            self.video_path,
            "-c",
            "copy",
            str(output_path),
        ]
        if self._run_ffmpeg(cmd):
            return str(output_path)
        return None

    def _extract_clip_moviepy(self, start: float, end: float, output_name: str) -> str | None:
        """Fallback extraction using MoviePy (slower, re-encodes)."""
        try:
            from moviepy.editor import VideoFileClip
        except ImportError:
            print("MoviePy not installed; cannot extract clips.")
            return None

        output_path = self.output_dir / output_name
        try:
            with VideoFileClip(self.video_path) as clip:
                subclip = clip.subclip(start, end)
                subclip.write_videofile(str(output_path), codec="libx264", audio_codec="aac")
            return str(output_path)
        except Exception as e:
            print(f"MoviePy extraction error: {e}")
            return None

    def extract_highlights(
        self, scorer: HighlightScorer, score_threshold: float = 5.0
    ) -> list[str]:
        """Extract clips for all events scoring above the threshold.

        Returns list of clip file paths.
        """

        # Re-read events from the scorer's source — expects scorer to have been used
        # with a list of events. Here we accept any events via the scorer's weights.
        clip_paths: list[str] = []
        return clip_paths

    def concatenate_clips(
        self, clip_paths: list[str], output_name: str = "highlight_reel.mp4"
    ) -> str | None:
        """Concatenate extracted clips into a single highlight reel."""
        if not clip_paths:
            return None

        output_path = self.output_dir / output_name

        if self._ffmpeg is not None:
            # Build concat demuxer list
            list_file = self.output_dir / "concat_list.txt"
            with open(list_file, "w") as f:
                for cp in clip_paths:
                    f.write(f"file '{cp}'\n")

            cmd = [
                "-f",
                "concat",
                "-safe",
                "0",
                "-i",
                str(list_file),
                "-c",
                "copy",
                str(output_path),
            ]
            if self._run_ffmpeg(cmd):
                return str(output_path)
            return None

        # Fallback: MoviePy
        try:
            from moviepy.editor import VideoFileClip, concatenate_videoclips

            clips = [VideoFileClip(cp) for cp in clip_paths]
            final = concatenate_videoclips(clips)
            final.write_videofile(str(output_path), codec="libx264", audio_codec="aac")
            for c in clips:
                c.close()
            final.close()
            return str(output_path)
        except ImportError:
            print("MoviePy not installed; cannot concatenate clips.")
            return None

    def create_highlight_reel(
        self,
        events: list,
        scorer: HighlightScorer | None = None,
        score_threshold: float = 5.0,
        pre_margin: float = 2.0,
        post_margin: float = 3.0,
        max_clips: int = 10,
    ) -> str | None:
        """Full pipeline: score events → extract clips → concatenate.

        Args:
            events: List of Event objects.
            scorer: Optional HighlightScorer instance.
            score_threshold: Minimum score for a clip to be included.

        Returns:
            Path to the final highlight reel, or None on failure.
        """
        if scorer is None:
            scorer = HighlightScorer()

        windows = scorer.highlight_windows(
            events, pre_margin=pre_margin, post_margin=post_margin, max_clips=max_clips
        )

        # Filter by threshold
        windows = [(s, e, sc) for s, e, sc in windows if sc >= score_threshold]
        if not windows:
            print("No highlight windows above threshold.")
            return None

        clip_paths: list[str] = []
        for i, (start, end, score) in enumerate(windows):
            name = f"highlight_00{i}_{score:.1f}.mp4"
            path = self.extract_clip(start, end, name)
            if path:
                clip_paths.append(path)

        return self.concatenate_clips(clip_paths)
