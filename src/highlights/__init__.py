"""
Highlights package.

Highlight scoring, clip extraction (FFmpeg/MoviePy), and audio spike analysis.
"""

from src.highlights.audio_analyzer import AudioAnalyzer
from src.highlights.ffmpeg_extractor import ClipExtractor
from src.highlights.scorer import HighlightScorer

__all__ = ["HighlightScorer", "ClipExtractor", "AudioAnalyzer"]
