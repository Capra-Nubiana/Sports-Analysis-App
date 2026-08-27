"""
Tests for model training pipeline (Phase 4).
"""

from scripts.train_model import TrainingPipeline


def test_training_pipeline_init():
    pipeline = TrainingPipeline(sport_name="football")
    assert pipeline.sport_name == "football"
    assert pipeline.config is not None


def test_build_train_config():
    pipeline = TrainingPipeline(sport_name="football")
    config = pipeline.build_train_config(
        dataset_path="/data/football",
        epochs=50,
        batch_size=8,
        img_size=640,
        learning_rate=0.001,
    )
    assert config["path"] == "/data/football"
    assert config["train"] == "images/train"
    assert config["val"] == "images/val"
    assert config["epochs"] == 50
    assert config["batch"] == 8
    assert config["imgsz"] == 640
    assert 0 in config["names"]
    assert 32 in config["names"]


def test_save_train_config(tmp_path):
    pipeline = TrainingPipeline(sport_name="football")
    config = pipeline.build_train_config(dataset_path="/data/test", epochs=10)
    output_path = str(tmp_path / "train_data.yaml")
    result = pipeline.save_train_config(config, output_path)
    assert result == output_path

    import os

    assert os.path.exists(result)


def test_training_pipeline_rugby():
    pipeline = TrainingPipeline(sport_name="rugby")
    config = pipeline.build_train_config(dataset_path="/data/rugby")
    assert config["names"][0] == "player"
    assert config["names"][32] == "ball"
