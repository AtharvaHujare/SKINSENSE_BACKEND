import tensorflow as tf
from pathlib import Path

MODEL_PATH = Path("models/model.keras")

_model = None


def load_model():
    global _model

    if _model is None:
        print("Loading model...")
        _model = tf.keras.models.load_model(MODEL_PATH)

    return _model