"""
Test core data models formatting and validation.
"""

from src.core.models import Detection, Player, Event, Match, SensorReading

def test_detection_model():
    d = Detection(bbox=[10.5, 20.0, 30.5, 40.0], class_id=0, confidence=0.85)
    assert d.class_id == 0
    assert d.confidence == 0.85
    assert len(d.bbox) == 4

def test_match_serialization():
    m = Match(sport_type="football", start_time="2026-01-01T12:00:00Z")
    p = Player(track_id=1, team_id=0)
    m.players[1] = p
    
    e = Event(event_type="goal", timestamp=120.5, frame_id=3600, confidence=0.9, players_involved=[1])
    m.add_event(e)
    
    json_data = m.model_dump_json()
    assert "football" in json_data
    assert "goal" in json_data
