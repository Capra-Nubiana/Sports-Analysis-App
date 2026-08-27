"""
Download script for YOLO model weights and other assets.
"""

import argparse
from pathlib import Path

DEFAULT_MODELS = [
    ("yolov8x.pt", "https://github.com/ultralytics/assets/releases/download/v0.0.0/yolov8x.pt"),
    ("yolo11x.pt", "https://github.com/ultralytics/assets/releases/download/v0.0.0/yolo11x.pt"),
]


def download_file(url: str, dest: Path) -> bool:
    """Download a single file, streaming to disk."""
    try:
        import requests
    except ImportError:
        import urllib.request

        try:
            urllib.request.urlretrieve(url, str(dest))  # noqa: S310
            print(f"Downloaded {dest.name} ({dest.stat().st_size} bytes)")
            return True
        except Exception as e:
            print(f"Failed to download {url}: {e}")
            return False

    try:
        response = requests.get(url, stream=True, timeout=60)
        response.raise_for_status()
        with open(dest, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        print(f"Downloaded {dest.name} ({dest.stat().st_size} bytes)")
        return True
    except Exception as e:
        print(f"Failed to download {url}: {e}")
        return False


def download_ultralytics_model(model_name: str = "yolov8x") -> Path | None:
    """Use Ultralytics built-in downloader if available."""
    try:
        from ultralytics import YOLO

        model = YOLO(model_name)
        return Path(model.model_path)
    except ImportError:
        print("ultralytics not installed; falling back to direct download.")
        return None
    except Exception as e:
        print(f"Model download failed: {e}")
        return None


def main() -> None:
    parser = argparse.ArgumentParser(description="Download model weights")
    parser.add_argument(
        "--models-dir",
        type=str,
        default="models",
        help="Output directory",
    )
    parser.add_argument(
        "--model",
        type=str,
        default=None,
        help="Specific model to download",
    )
    args = parser.parse_args()

    models_dir = Path(args.models_dir)
    models_dir.mkdir(exist_ok=True)

    if args.model:
        names = [args.model]
    else:
        names = [name for name, _ in DEFAULT_MODELS]

    for name in names:
        dest = models_dir / name
        if dest.exists() and dest.stat().st_size > 0:
            print(f"{name} already exists, skipping.")
            continue
        download_ultralytics_model(name)
        if dest.exists():
            continue
        url = next((u for n, u in DEFAULT_MODELS if n == name), None)
        if url:
            download_file(url, dest)

    print(f"All models downloaded to {models_dir}")


if __name__ == "__main__":
    main()
