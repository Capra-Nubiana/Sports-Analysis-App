"""
Main Analysis Pipeline Orchestrator
Depends entirely on abstractions (DataSource, Detector, Tracker).
"""

import argparse
import time
from pathlib import Path
from typing import cast

from src.core.factory import ComponentFactory
from src.core.models import Match, Player
from src.ingest.video_source import VideoFrame
from src.spatial.homography import HomographyMapper


class Pipeline:
    def __init__(self, sport_name: str, video_path: str, generate_highlights: bool = False) -> None:
        self.sport_name = sport_name
        self.video_path = video_path
        self.generate_highlights = generate_highlights

        # Dependency Injection via Factory
        self.factory = ComponentFactory(sport_name)

        # Instantiate Components
        self.video_source = self.factory.create_video_source(video_path)
        self.detector = self.factory.create_detector()
        self.tracker = self.factory.create_tracker()
        self.team_classifier = self.factory.create_team_classifier()
        self.event_detector = self.factory.create_event_detector()

        # Spatial mapping for event detection
        self.homography = self._setup_homography()

        # Highlight generation (Phase 2)
        self.scorer = None
        self.extractor = None
        if generate_highlights:
            from src.highlights.ffmpeg_extractor import ClipExtractor
            from src.highlights.scorer import HighlightScorer

            self.scorer = HighlightScorer(self.factory.config)
            self.extractor = ClipExtractor(video_path)

        # Main Data Container
        self.match_data = Match(
            sport_type=sport_name,
            start_time=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        )

    def _setup_homography(self) -> HomographyMapper:
        """Load homography from config keypoints if available."""
        homography = HomographyMapper()
        keypoints = self.factory.config.get("spatial.keypoints")
        if keypoints:
            src_pts = [(kp["x"], kp["y"]) for kp in keypoints]
            dst_pts = [(kp["mx"], kp["my"]) for kp in keypoints]
            if len(src_pts) >= 4:
                homography.calibrate(src_pts, dst_pts)
        return homography

    def run(self) -> None:
        """Run the main analysis loop over all frames."""
        print(f"Starting {self.sport_name} analysis on {self.video_path}")

        if not self.video_source.open():
            raise RuntimeError(f"Failed to open video source: {self.video_path}")

        try:
            for raw_frame in self.video_source.iter_frames():
                frame = cast(VideoFrame, raw_frame)
                # 1. Detect
                raw_detections = self.detector.detect(frame.image)

                # 2. Track
                tracked_detections = self.tracker.update(raw_detections, frame.image)

                # 3. Classify Teams & Update Match Model
                for det in tracked_detections:
                    team_id = self.team_classifier.classify(det, frame.image)
                    if det.track_id not in self.match_data.players:
                        self.match_data.players[det.track_id] = Player(
                            track_id=det.track_id,
                            team_id=team_id,
                        )
                    # Update positions
                    # self.match_data.players[det.track_id].positions_2d[frame.timestamp] = ...

                # 4. Detect Events (Phase 2)
                if self.event_detector is not None:
                    events = self.event_detector.process_frame(
                        tracked_detections, self.homography, frame.timestamp, frame.frame_id
                    )
                    for event in events:
                        self.match_data.add_event(event)

                # Progress callback
                if frame.frame_id % 100 == 0:
                    print(f"Processed frame {frame.frame_id} (t={frame.timestamp:.2f}s)")

        finally:
            self.video_source.close()

        # Output final match JSON
        self.export_timeline()

        # Generate highlights (Phase 2)
        if self.generate_highlights:
            self.generate_highlight_reel()

    def export_timeline(self) -> None:
        """Export the Match data to JSON."""
        output_dir = Path("output")
        output_dir.mkdir(exist_ok=True)
        out_file = output_dir / f"timeline_{Path(self.video_path).stem}.json"
        with open(out_file, "w") as f:
            f.write(self.match_data.model_dump_json(indent=2))
        print(f"Timeline exported to {out_file}")

    def generate_highlight_reel(self) -> None:
        """Score events and extract highlight clips."""
        if self.scorer is None or self.extractor is None:
            return

        print("Generating highlight reel...")
        reel_path = self.extractor.create_highlight_reel(self.match_data.events, self.scorer)
        if reel_path:
            print(f"Highlight reel saved to {reel_path}")
        else:
            print("No highlights generated (no events or clips failed).")


def main() -> None:
    parser = argparse.ArgumentParser(description="Run Sports Analysis Pipeline")
    parser.add_argument(
        "--sport", type=str, required=True, help="Sport config (football, rugby, basketball)"
    )
    parser.add_argument("--video", type=str, required=True, help="Path to video file")
    parser.add_argument(
        "--highlights", action="store_true", help="Generate highlight reel from detected events"
    )

    args = parser.parse_args()

    pipeline = Pipeline(
        sport_name=args.sport,
        video_path=args.video,
        generate_highlights=args.highlights,
    )
    pipeline.run()


if __name__ == "__main__":
    main()
