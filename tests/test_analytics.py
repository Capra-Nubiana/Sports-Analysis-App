"""
Tests for analytics package (Phase 3).
"""

from src.analytics.distance import DistanceAnalyzer
from src.analytics.heatmap import HeatmapGenerator
from src.analytics.report import AnalyticsReport
from src.analytics.sprint import SprintDetector
from src.core.models import Match, Player


def test_heatmap_empty_positions():
    gen = HeatmapGenerator()
    result = gen.generate([])
    assert result["total_points"] == 0
    assert result["grid"] == []


def test_heatmap_with_positions():
    gen = HeatmapGenerator(pitch_size=(10.0, 10.0), bins=10)
    positions = [(5.0, 5.0), (5.0, 5.0), (8.0, 8.0)]
    result = gen.generate(positions)
    assert result["total_points"] == 3
    assert result["max_density"] > 0


def test_distance_analyzer_short_track():
    analyzer = DistanceAnalyzer(frame_rate=30.0)
    result = analyzer.analyze([(0, 0, 0.0), (3.0, 4.0, 1.0)])
    assert result["total_distance_m"] == 5.0
    assert result["average_speed_ms"] == 5.0


def test_distance_analyzer_empty():
    analyzer = DistanceAnalyzer()
    result = analyzer.analyze([])
    assert result["total_distance_m"] == 0.0


def test_sprint_detector():
    detector = SprintDetector(sprint_speed_threshold=3.0, min_duration=0.5)
    positions = [
        (0.0, 0.0, 0.0),
        (5.0, 0.0, 0.5),
        (10.0, 0.0, 1.0),
        (15.0, 0.0, 1.5),
        (15.0, 0.0, 2.0),
    ]
    sprints = detector.detect(positions)
    assert len(sprints) >= 1
    assert "start_time" in sprints[0]
    assert "distance_m" in sprints[0]


def test_sprint_detector_short_burst_filtered():
    detector = SprintDetector(sprint_speed_threshold=3.0, min_duration=5.0)
    positions = [
        (0.0, 0.0, 0.0),
        (10.0, 0.0, 1.0),
    ]
    sprints = detector.detect(positions)
    assert len(sprints) == 0


def test_analytics_report_player_not_found():
    match = Match(sport_type="football", start_time="2026-01-01T00:00:00Z")
    report = AnalyticsReport(match)
    result = report.generate_player_report(999)
    assert "error" in result


def test_analytics_report_full():
    match = Match(
        sport_type="football",
        start_time="2026-01-01T00:00:00Z",
        players={
            1: Player(
                track_id=1,
                team_id=0,
                positions_2d={0.0: (0.0, 0.0), 1.0: (5.0, 0.0), 2.0: (10.0, 0.0)},
            )
        },
        events=[],
    )
    report = AnalyticsReport(match)
    result = report.generate_full_report()
    assert result["total_players"] == 1
    assert result["total_events"] == 0
    assert "player_reports" in result
    assert len(result["player_reports"]) == 1
