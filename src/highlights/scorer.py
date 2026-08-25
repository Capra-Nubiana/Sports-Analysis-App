"""
Highlight Scoring Engine

Ranks match events by importance and identifies the best
timestamp windows for highlight clip generation.
"""

from src.core.models import Event
from src.core.sport_config import SportConfig


class HighlightScorer:
    """Scores events and produces candidate highlight time ranges."""

    # Default per-event-type weights (higher = more important)
    DEFAULT_WEIGHTS: dict[str, float] = {
        "goal": 10.0,
        "try_scored": 10.0,
        "tackle": 6.0,
        "scored_basket": 8.0,
        "three_pointer": 7.0,
        "pass": 2.0,
        "scrum": 3.0,
    }

    def __init__(self, config: SportConfig | None = None, weights: dict[str, float] | None = None):
        self.config = config
        self.weights = {**self.DEFAULT_WEIGHTS}
        if weights:
            self.weights.update(weights)

    def score_event(self, event: Event) -> float:
        """Compute a numeric importance score for a single event."""
        base = self.weights.get(event.event_type, 1.0)
        # Boost by confidence
        score = base * event.confidence
        return round(score, 3)

    def score_events(self, events: list[Event]) -> list[tuple[Event, float]]:
        """Score all events, returning (event, score) pairs sorted by score desc."""
        scored = [(e, self.score_event(e)) for e in events]
        scored.sort(key=lambda x: x[1], reverse=True)
        return scored

    def highlight_windows(
        self,
        events: list[Event],
        pre_margin: float = 2.0,
        post_margin: float = 3.0,
        max_clips: int = 10,
    ) -> list[tuple[float, float, float]]:
        """Generate (start, end, score) windows for the best highlight clips.

        Args:
            events: List of detected match events.
            pre_margin: Seconds before the event to include in the clip.
            post_margin: Seconds after the event to include.
            max_clips: Maximum number of windows to return.

        Returns:
            List of (start_time, end_time, score) tuples, sorted by score desc.
        """
        scored = self.score_events(events)
        windows: list[tuple[float, float, float]] = []

        for event, score in scored:
            start = max(0.0, event.timestamp - pre_margin)
            end = event.timestamp + post_margin

            # Skip windows that overlap significantly with already-selected clips
            overlaps = any(not (end < w_start or start > w_end) for w_start, w_end, _ in windows)
            if overlaps:
                continue

            windows.append((start, end, score))
            if len(windows) >= max_clips:
                break

        return windows
