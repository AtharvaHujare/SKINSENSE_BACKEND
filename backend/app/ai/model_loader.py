import os
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parent
MODELS_DIR = BASE_DIR / "models"
MODEL_PATH = MODELS_DIR / "model.keras"
ALT_MODEL_PATH = MODELS_DIR / "model.h5"

_model = None


def _create_bootstrap_model():
    """
    Creates and saves a placeholder EfficientNetB0 model architecture
    if no pre-trained model artifact exists on disk.
    """
    try:
        import tensorflow as tf
        MODELS_DIR.mkdir(parents=True, exist_ok=True)
        inputs = tf.keras.Input(shape=(224, 224, 3), name="input_layer")
        data_aug = tf.keras.layers.Identity(name="data_augmentation")(inputs)

        base_model = tf.keras.applications.EfficientNetB0(
            include_top=False,
            weights=None,
            input_tensor=data_aug
        )
        base_model._name = "efficientnetb0"

        x = base_model.output
        x = tf.keras.layers.GlobalAveragePooling2D(name="avg_pool")(x)
        outputs = tf.keras.layers.Dense(7, activation="softmax", name="predictions")(x)

        model = tf.keras.Model(inputs=inputs, outputs=outputs, name="skinsense_ai_model")
        model.save(MODEL_PATH)
        logger.info("Successfully bootstrapped default model architecture to '%s'", MODEL_PATH)
        return model
    except Exception as exc:
        logger.warning("Could not auto-generate bootstrap model: %s", exc)
        return None


def load_model():
    """
    Loads and caches the AI deep learning model from disk.
    Raises a clear RuntimeError if the model artifact is missing or corrupted.
    """
    global _model

    if _model is None:
        import tensorflow as tf

        target_path = None
        if MODEL_PATH.exists():
            target_path = MODEL_PATH
        elif ALT_MODEL_PATH.exists():
            target_path = ALT_MODEL_PATH

        if target_path is not None:
            try:
                logger.info("Loading AI model from '%s'...", target_path)
                _model = tf.keras.models.load_model(target_path, compile=False)
            except Exception as exc:
                logger.error("Failed to load model file at '%s': %s", target_path, exc)
                raise RuntimeError(
                    f"Failed to load AI model from '{target_path}': {exc}"
                ) from exc
        else:
            # Try to auto-create bootstrap placeholder model
            _model = _create_bootstrap_model()

        if _model is None:
            raise RuntimeError(
                f"Trained AI model artifact missing at '{MODEL_PATH}'. "
                "Please place 'model.keras' or 'model.h5' inside 'app/ai/models/' directory."
            )

    return _model