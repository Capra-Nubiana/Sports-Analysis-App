"""
Tests for highlight scoring and audio analysis (Phase 2).
"""

from src.core.models import Event
from src.highlights.ffmpeg_extractor import ClipExtractor
from src.highlights.scorer import HighlightScorer


def _make_event(event_type: str, timestamp: float, confidence: float = 0.9) -> Event:
    return Event(
        event_type=event_type,
        timestamp=timestamp,
        frame_id=int(timestamp * 30),
        confidence=confidence,
        players_involved=[1, 2],
        metadata={},
    )


def test_scorer_scores_goal_higher():
    scorer = HighlightScorer()
    goal = _make_event("goal", 100.0, 0.9)
    pass_ = _make_event("pass", 50.0, 0.8)
    assert scorer.score_event(goal) > scorer.score_event(pass_)


def test_scorer_returns_sorted():
    scorer = HighlightScorer()
    events = [
        _make_event("pass", 10.0, 0.5),
        _make_event("goal", 100.0, 0.95),
        _make_event("tackle", 50.0, 0.8),
    ]
    scored = scorer.score_events(events)
    assert scored[0][0].event_type == "goal"
    assert scored[-1][0].event_type == "pass"


def test_highlight_windows_no_overlap():
    scorer = HighlightScorer()
    events = [
        _make_event("goal", 10.0, 0.9),
        _make_event("goal", 11.0, 0.9),  # overlaps with first
        _make_event("goal", 50.0, 0.9),
    ]
    windows = scorer.highlight_windows(events, pre_margin=2.0, post_margin=3.0, max_clips=5)
    assert len(windows) == 2  # second event overlaps first, so filtered


def test_highlight_windows_max_clips():
    scorer = HighlightScorer()
    events = [_make_event("goal", float(i * 10), 0.9) for i in range(20)]
    windows = scorer.highlight_windows(events, max_clips=3)
    assert len(windows) <= 3


def test_clip_extractor_no_video():
    extractor = ClipExtractor("nonexistent_video.mp4")
    assert extractor.video_path == "nonexistent_video.mp4"
    # Should not crash, just return None
    result = extractor.extract_clip(0, 5, "test.mp4")
    assert result is None or isinstance(result, str)


def test_scorer_custom_weights():
    scorer = HighlightScorer(weights={"goal": 5.0})
    goal = _make_event("goal", 0.0, 1.0)
    # base (5.0) * confidence (1.0) = 5.0
    assert scorer.score_event(goal) == 5.0
