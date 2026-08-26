"""
Analytics Report Generator

Aggregates heatmap, distance, and sprint analysis into
a comprehensive per-player report.
"""

from typing import Any

from src.analytics.distance import DistanceAnalyzer
from src.analytics.heatmap import HeatmapGenerator
from src.analytics.sprint import SprintDetector
from src.core.models import Match


class AnalyticsReport:
    """Generates comprehensive analytics reports from match data."""

    def __init__(self, match: Match):
        self.match = match
        self.heatmap_gen = HeatmapGenerator()
        self.distance_analyzer = DistanceAnalyzer()
        self.sprint_detector = SprintDetector()

    def generate_player_report(self, track_id: int) -> dict[str, Any]:
        """Generate a full analytics report for a single player."""
        if track_id not in self.match.players:
            return {"error": f"Player {track_id} not found"}

        player = self.match.players[track_id]

        # Convert positions_2d dict to sorted list of (x, y, timestamp)
        positions: list[tuple[float, float, float]] = []
        if player.positions_2d:
            positions = sorted(
                [(x, y, t) for t, (x, y) in player.positions_2d.items()],
                key=lambda p: p[2],
            )

        xy_positions = [(p[0], p[1]) for p in positions]

        heatmap_data = self.heatmap_gen.generate(xy_positions)
        distance_data = self.distance_analyzer.analyze(positions)
        sprint_data = self.sprint_detector.detect(positions)

        return {
            "track_id": track_id,
            "team_id": player.team_id,
            "heatmap": heatmap_data,
            "distance": distance_data,
            "sprints": sprint_data,
        }

    def generate_full_report(self) -> dict[str, Any]:
        """Generate analytics reports for all players."""
        reports: list[dict[str, Any]] = []
        for track_id in self.match.players:
            report = self.generate_player_report(track_id)
            reports.append(report)

        return {
            "sport_type": self.match.sport_type,
            "total_players": len(self.match.players),
            "total_events": len(self.match.events),
            "player_reports": reports,
        }
