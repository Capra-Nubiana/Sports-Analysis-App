"""
PyTorch Model Training Pipeline

Fine-tunes YOLOv8/v11 models on sport-specific datasets using
the Ultralytics training API. Configurable via YAML or CLI.
"""

import argparse
from pathlib import Path
from typing import Any

import yaml

from src.core.sport_config import SportConfig


class TrainingPipeline:
    """Encapsulates model fine-tuning configuration and execution."""

    def __init__(self, sport_name: str, config_dir: str = "config"):
        self.config = SportConfig(sport_name, config_dir)
        self.sport_name = sport_name

    def build_train_config(
        self,
        dataset_path: str,
        epochs: int = 100,
        batch_size: int = 16,
        img_size: int = 640,
        learning_rate: float = 0.001,
    ) -> dict[str, Any]:
        """Generate the training YAML data dict for Ultralytics."""
        classes = self.config.data.get("detection.classes", [0, 32])

        config: dict[str, Any] = {
            "path": dataset_path,
            "train": "images/train",
            "val": "images/val",
            "names": {
                0: "player",
                1: "referee",
                2: "goalkeeper",
                32: "ball",
            },
            "epochs": epochs,
            "batch": batch_size,
            "imgsz": img_size,
            "lr0": learning_rate,
            "train_split_ratio": self.config.data.get("detection.train_split_ratio", 0.8),
            "classes": classes,
        }

        return config

    def save_train_config(self, config: dict[str, Any], output_path: str) -> str:
        """Save the training config as a YAML file."""
        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w") as f:
            yaml.dump(config, f, default_flow_style=False)
        return str(path)

    def train(
        self,
        dataset_path: str,
        model_path: str = "yolov8x.pt",
        output_name: str = "custom",
        epochs: int = 100,
        batch_size: int = 16,
        img_size: int = 640,
        learning_rate: float = 0.001,
        project: str = "runs/train",
        patience: int = 20,
        device: str | None = None,
    ) -> str | None:
        """Run model fine-tuning.

        Returns the output directory path on success, None on failure.
        """
        train_config = self.build_train_config(
            dataset_path=dataset_path,
            epochs=epochs,
            batch_size=batch_size,
            img_size=img_size,
            learning_rate=learning_rate,
        )

        config_path = self.save_train_config(
            train_config, str(Path(project) / f"{output_name}_data.yaml")
        )

        try:
            import torch
            from ultralytics import YOLO
        except ImportError:
            print("ultralytics or torch not installed; cannot train.")
            return None

        model = YOLO(model_path)

        if device is None:
            device = "cuda" if torch.cuda.is_available() else "cpu"

        model.train(
            data=config_path,
            epochs=epochs,
            batch=batch_size,
            imgsz=img_size,
            lr0=learning_rate,
            name=output_name,
            project=project,
            patience=patience,
            device=device,
            verbose=True,
        )

        output_dir = Path(project) / output_name
        return str(output_dir)

    def validate(self, model_path: str, dataset_path: str) -> dict[str, float] | None:
        """Run validation on a trained model and return metrics."""
        try:
            from ultralytics import YOLO
        except ImportError:
            print("ultralytics not installed; cannot validate.")
            return None

        train_config = self.build_train_config(dataset_path=dataset_path)
        config_path = self.save_train_config(
            train_config, str(Path("runs/val") / f"{self.sport_name}_val.yaml")
        )

        model = YOLO(model_path)
        metrics = model.val(data=config_path, verbose=False)

        return {
            "mAP50": float(metrics.box.map50),
            "mAP50_95": float(metrics.box.map),
            "precision": float(metrics.box.p),
            "recall": float(metrics.box.r),
        }


def main() -> None:
    parser = argparse.ArgumentParser(description="Train a YOLO model for sports analysis")
    parser.add_argument(
        "--sport", type=str, required=True, help="Sport name (football, rugby, basketball)"
    )
    parser.add_argument("--dataset", type=str, required=True, help="Path to dataset (YOLO format)")
    parser.add_argument("--model", type=str, default="yolov8x.pt", help="Base model path")
    parser.add_argument("--epochs", type=int, default=100, help="Number of training epochs")
    parser.add_argument("--batch-size", type=int, default=16, help="Batch size")
    parser.add_argument("--img-size", type=int, default=640, help="Image size")
    parser.add_argument("--lr", type=float, default=0.001, help="Learning rate")
    parser.add_argument("--project", type=str, default="runs/train", help="Output project dir")
    parser.add_argument("--name", type=str, default="custom", help="Run name")
    parser.add_argument(
        "--validate",
        type=str,
        default=None,
        help="Validate a trained model on a dataset (provide model path)",
    )

    args = parser.parse_args()

    pipeline = TrainingPipeline(sport_name=args.sport)

    if args.validate:
        metrics = pipeline.validate(args.validate, args.dataset)
        if metrics:
            print("Validation results:")
            for k, v in metrics.items():
                print(f"  {k}: {v:.4f}")
    else:
        result = pipeline.train(
            dataset_path=args.dataset,
            model_path=args.model,
            output_name=args.name,
            epochs=args.epochs,
            batch_size=args.batch_size,
            img_size=args.img_size,
            learning_rate=args.lr,
            project=args.project,
        )
        if result:
            print(f"Training complete. Output: {result}")


if __name__ == "__main__":
    main()
