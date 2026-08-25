"""
Audio Spike Analysis

Detects crowd noise spikes in video audio tracks using LibROSA,
which can be used as an additional signal for highlight scoring.
"""

import numpy as np


class AudioAnalyzer:
    """Analyzes audio tracks for crowd noise spikes (excitement moments)."""

    def __init__(self, hop_length: int = 512, top_db: float = 20.0):
        self.hop_length = hop_length
        self.top_db = top_db

    def extract_audio(self, video_path: str, output_path: str | None = None) -> str | None:
        """Extract audio track from video using FFmpeg or MoviePy."""
        import shutil
        import subprocess
        from pathlib import Path

        video_path = str(video_path)
        if output_path is None:
            output_path = str(Path(video_path).with_suffix(".wav"))

        ffmpeg = shutil.which("ffmpeg")
        if ffmpeg is None:
            try:
                from imageio_ffmpeg import get_ffmpeg_exe

                ffmpeg = get_ffmpeg_exe()
            except ImportError:
                return self._extract_audio_moviepy(video_path, output_path)

        cmd = [
            ffmpeg,
            "-y",
            "-i",
            video_path,
            "-vn",
            "-acodec",
            "pcm_s16le",
            "-ar",
            "22050",
            "-ac",
            "1",
            output_path,
        ]
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)  # noqa: S603
            if result.returncode == 0:
                return output_path
            print(f"FFmpeg audio extraction failed: {result.stderr}")
        except Exception as e:
            print(f"Audio extraction error: {e}")

        return self._extract_audio_moviepy(video_path, output_path)

    def _extract_audio_moviepy(self, video_path: str, output_path: str) -> str | None:
        """Fallback audio extraction via MoviePy."""
        try:
            from moviepy.editor import VideoFileClip

            with VideoFileClip(video_path) as clip:
                if clip.audio is not None:
                    clip.audio.write_audiofile(output_path)
                    return output_path
        except ImportError:
            print("MoviePy not installed; cannot extract audio.")
        except Exception as e:
            print(f"MoviePy audio extraction error: {e}")
        return None

    def detect_spikes(
        self, video_path: str, sample_rate: int = 22050, spike_threshold_db: float = 15.0
    ) -> list[tuple[float, float]]:
        """Detect audio amplitude spikes in a video's audio track.

        Args:
            video_path: Path to the input video file.
            sample_rate: Target audio sample rate.
            spike_threshold_db: dB above the mean RMS to count as a spike.

        Returns:
            List of (timestamp_sec, rms_db) tuples for detected spikes.
        """
        import librosa

        audio_path = self.extract_audio(video_path)
        if audio_path is None:
            return []

        try:
            y, sr = librosa.load(audio_path, sr=sample_rate, mono=True)
        except Exception as e:
            print(f"Failed to load audio: {e}")
            return []

        # Compute RMS energy over time
        rms = librosa.feature.rms(
            y=y, hop_length=self.hop_length, frame_length=self.hop_length * 4
        )[0]
        rms_db = librosa.amplitude_to_db(rms, ref=np.max)

        times = librosa.frames_to_time(np.arange(len(rms_db)), sr=sr, hop_length=self.hop_length)

        # Mean + threshold for spike detection
        mean_db = float(np.mean(rms_db))
        spikes: list[tuple[float, float]] = []

        for t, db in zip(times, rms_db, strict=False):
            if db > mean_db + spike_threshold_db:
                spikes.append((float(t), float(db)))

        # Deduplicate: keep only one spike per 2-second window
        deduped: list[tuple[float, float]] = []
        last_time = -10.0
        for t, db in spikes:
            if t - last_time >= 2.0:
                deduped.append((t, db))
                last_time = t

        return deduped

    def score_by_audio(
        self, events: list, spikes: list[tuple[float, float]], window_sec: float = 3.0
    ) -> dict[int, float]:
        """Boost event scores based on nearby audio spikes.

        Args:
            events: List of Event objects.
            spikes: Output from detect_spikes().
            window_sec: Look for spikes within this window around each event.

        Returns:
            Dict mapping event index to audio spike count.
        """
        scores: dict[int, float] = {}
        for i, event in enumerate(events):
            count = sum(1 for spike_t, _ in spikes if abs(spike_t - event.timestamp) <= window_sec)
            scores[i] = float(count)
        return scores
