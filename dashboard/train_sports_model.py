#!/usr/bin/env python3
"""
Sports Analysis Model Training — Colab-Compatible Script

Usage (in Colab):
    !python train_sports_model.py --sport rugby --epochs 100 --batch-size 16

This script downloads datasets directly from Roboflow API and trains a YOLO
model without manual dataset download.

Requirements:
    pip install roboflow ultralytics torch
"""

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path


ROBOFLOW_API_KEY = os.environ.get("ROBOFLOW_API_KEY", "")


def install_packages():
    """Install required packages (for Colab)."""
    packages = ["roboflow", "ultralytics", "torch"]
    subprocess.check_call([sys.executable, "-m", "pip", "install"] + packages)


def get_dataset_config(sport: str) -> dict:
    """Get dataset configuration for a sport.

    All workspace/project pairs verified against Roboflow Universe search
    results and the class names below match what each version exports as
    YOLO TXT labels (class-index order in data.yaml must correspond).
    """
    configs = {
        "rugby": {
            "workspace": "jfc",
            "project": "rugby-matches",
            "version": 2,
            "classes": {
                0: "ball",
                1: "player",
                2: "referee",
            },
            "model": "yolov8x.pt",
            "imgsz": 1280,
        },
    }
    return configs.get(sport, configs["rugby"])


def download_roboflow_dataset(workspace: str, project: str, version: int) -> Path:
    """Download full dataset from Roboflow API (train + valid splits included).

    Roboflow's Python SDK returns the entire version as a single download
    with subfolders: <project>/train, <project>/valid, <project>/test
    The format argument ("yolo") controls label format, not split.
    """
    from roboflow import Roboflow

    rf = Roboflow(api_key=ROBOFLOW_API_KEY)
    proj = rf.workspace(workspace).project(project)
    version_obj = proj.version(version)
    path = version_obj.download("yolo")
    return Path(path)


def create_data_yaml(output_dir: Path, dataset_dir: Path, classes: dict[int, str]) -> Path:
    """Create YOLO data.yaml configuration file.

    Roboflow's YOLO download places data in <dataset_dir>/train, /valid, /test.
    We point the yaml at those subdirectories and override class IDs to match
    the canonical ordering expected by the pipeline.
    """
    yaml_content = f"""path: {dataset_dir}

train: {dataset_dir}/train
val: {dataset_dir}/valid"""

    if (dataset_dir / "test").exists():
        yaml_content += f"\ntest: {dataset_dir}/test"

    yaml_content += f"""

nc: {len(classes)}
names:"""
    for idx, name in sorted(classes.items()):
        yaml_content += f"\n  {idx}: {name}"

    yaml_path = output_dir / "data.yaml"
    with open(yaml_path, "w") as f:
        f.write(yaml_content)
    return yaml_path


def train_model(args):
    """Download dataset and train YOLO model."""
    if not ROBOFLOW_API_KEY:
        print("ERROR: Set ROBOFLOW_API_KEY environment variable")
        print("Get a key from: https://app.roboflow.com/")
        return

    install_packages()

    dataset_config = get_dataset_config(args.sport)

    print(f"Downloading dataset for {args.sport}...")
    print(f"  Project: {dataset_config['project']}")
    print(f"  Classes: {list(dataset_config['classes'].values())}")

    dataset_dir = download_roboflow_dataset(
        workspace=dataset_config["workspace"],
        project=dataset_config["project"],
        version=dataset_config["version"],
    )
    print(f"  Downloaded to: {dataset_dir}")

    output_dir = Path("/content/datasets") / args.sport
    output_dir.mkdir(parents=True, exist_ok=True)

    yaml_path = create_data_yaml(output_dir, dataset_dir, dataset_config["classes"])
    print(f"\nDataset config written to {yaml_path}")

    from ultralytics import YOLO
    import torch

    print(f"\nStarting training...")
    print(f"  Model: {dataset_config['model']}")
    print(f"  Epochs: {args.epochs}")
    print(f"  Batch size: {args.batch_size}")
    print(f"  Image size: {dataset_config['imgsz']}")

    device = "cuda" if torch.cuda.is_available() else "cpu"

    model = YOLO(dataset_config["model"])

    results = model.train(
        data=str(yaml_path),
        epochs=args.epochs,
        batch=args.batch_size,
        imgsz=dataset_config["imgsz"],
        patience=20,
        augment=True,
        mosaic=1.0,
        degrees=10.0,
        translate=0.1,
        scale=0.5,
        fliplr=0.5,
        project="/content/runs/train",
        name=f"{args.sport}-v1",
        device=device,
        amp=True,
    )

    print(f"\n{'='*60}")
    print("Validation Results")
    print(f"{'='*60}")
    metrics = model.val(data=str(yaml_path))
    print(f"  mAP@0.5:        {metrics.box.map50:.4f}")
    print(f"  mAP@0.5:0.95:   {metrics.box.map:.4f}")
    print(f"  Precision:      {metrics.box.p:.4f}")
    print(f"  Recall:         {metrics.box.r:.4f}")

    best_model = Path("/content/runs/train") / f"{args.sport}-v1" / "weights" / "best.pt"
    export_dir = Path(f"/content/models/{args.sport}/")
    export_dir.mkdir(parents=True, exist_ok=True)

    if best_model.exists():
        shutil.copy(best_model, export_dir / "best.pt")
        model.export(format="onnx", weights=str(best_model), save_dir=str(export_dir))
        print(f"\nModel exported to {export_dir}")
    else:
        model.export(format="onnx", save_dir=str(export_dir))
        print(f"\nModel exported to {export_dir}")

    return results


def main():
    parser = argparse.ArgumentParser(
        description="Train YOLO model for sports analysis from Roboflow datasets"
    )
    parser.add_argument(
        "--sport",
        type=str,
        required=True,
        choices=["rugby"],
        help="Sport to train for",
    )
    parser.add_argument("--epochs", type=int, default=100, help="Training epochs")
    parser.add_argument("--batch-size", type=int, default=16, help="Batch size")
    parser.add_argument(
        "--roboflow-key",
        type=str,
        default=None,
        help="Roboflow API key (or set ROBOFLOW_API_KEY env var)",
    )

    args = parser.parse_args()

    if args.roboflow_key:
        os.environ["ROBOFLOW_API_KEY"] = args.roboflow_key

    train_model(args)


if __name__ == "__main__":
    main()
