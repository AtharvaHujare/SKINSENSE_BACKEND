import tensorflow as tf
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
MODEL_PATH = BASE_DIR / "models" / "model.keras"

_model = None


def load_model():
    global _model

    if _model is None:
        print("Loading model...")
        _model = tf.keras.models.load_model(MODEL_PATH)

    return _model