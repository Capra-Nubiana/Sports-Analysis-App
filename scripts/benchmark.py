"""
Benchmark script for evaluating model inference speed.
"""

import argparse
import time

import numpy as np


class Benchmark:
    """Run a simple inference/processing benchmark on video sources or models."""

    def __init__(self, sport: str = "football"):
        self.sport = sport

    def benchmark_detector(
        self, model_path: str = "models/yolov8x.pt", iterations: int = 10
    ) -> dict:
        """Benchmark YOLO detector inference on random images."""
        try:
            from src.detection.detector import YOLODetector
        except Exception as e:
            print(f"Cannot import detector: {e}")
            return {}

        detector = YOLODetector(model_path=model_path)
        if detector.model is None:
            print("Detector model not loaded; skipping benchmark.")
            return {"error": "model_not_loaded"}

        dummy_images = [np.zeros((640, 640, 3), dtype=np.uint8) for _ in range(iterations)]

        start = time.perf_counter()
        for img in dummy_images:
            _ = detector.detect(img)
        elapsed = time.perf_counter() - start

        avg_ms = (elapsed / iterations) * 1000
        fps = iterations / elapsed
        return {"avg_ms": round(avg_ms, 2), "fps": round(fps, 2), "iterations": iterations}

    def benchmark_pipeline(self, video_path: str, max_frames: int = 100) -> dict:
        """Benchmark end-to-end pipeline frame processing."""
        try:
            from src.core.factory import ComponentFactory
        except Exception as e:
            print(f"Cannot import factory: {e}")
            return {}

        factory = ComponentFactory(self.sport)
        video_source = factory.create_video_source(video_path)

        if not video_source.open():
            return {"error": "video_not_opened"}

        detector = factory.create_detector()
        tracker = factory.create_tracker()

        frame_count = 0
        start = time.perf_counter()
        try:
            from typing import cast

            from src.ingest.video_source import VideoFrame

            for raw_frame in video_source.iter_frames():
                if frame_count >= max_frames:
                    break
                frame = cast(VideoFrame, raw_frame)
                detections = detector.detect(frame.image)
                _ = tracker.update(detections, frame.image)
                frame_count += 1
        finally:
            video_source.close()

        elapsed = time.perf_counter() - start
        fps = frame_count / elapsed if elapsed > 0 else 0
        return {"frames": frame_count, "time_sec": round(elapsed, 3), "fps": round(fps, 2)}


def main() -> None:
    parser = argparse.ArgumentParser(description="Benchmark inference performance")
    parser.add_argument("--sport", type=str, default="football", help="Sport config name")
    parser.add_argument("--video", type=str, default=None, help="Video file to benchmark")
    parser.add_argument("--model", type=str, default="models/yolov8x.pt", help="Model path")
    parser.add_argument("--iterations", type=int, default=10, help="Number of inference iterations")
    parser.add_argument(
        "--max-frames", type=int, default=100, help="Max frames for pipeline benchmark"
    )
    args = parser.parse_args()

    bench = Benchmark(sport=args.sport)

    if args.video:
        print(f"Benchmarking pipeline on {args.video}...")
        result = bench.benchmark_pipeline(args.video, max_frames=args.max_frames)
        print(f"Result: {result}")
    else:
        print(f"Benchmarking detector with {args.iterations} iterations...")
        result = bench.benchmark_detector(args.model, iterations=args.iterations)
        print(f"Result: {result}")


if __name__ == "__main__":
    main()
