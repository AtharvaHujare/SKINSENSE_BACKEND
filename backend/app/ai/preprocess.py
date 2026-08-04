import json
import logging
from pathlib import Path

import numpy as np
import tensorflow as tf
from PIL import Image

logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parent
CONFIG_PATH = BASE_DIR / "models" / "config.json"

DEFAULT_CONFIG = {
    "image_size": 224,
    "model_version": "v1.0.0",
    "normalization": "rescale_255"
}

if CONFIG_PATH.exists():
    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            CONFIG = json.load(f)
    except Exception as exc:
        logger.warning("Could not read config.json at '%s': %s. Falling back to default config.", CONFIG_PATH, exc)
        CONFIG = DEFAULT_CONFIG
else:
    CONFIG = DEFAULT_CONFIG

IMAGE_SIZE = CONFIG.get("image_size", 224)


def preprocess_image(image_path):
    """
    Preprocesses an input lesion image:
    1. Opens image and converts to RGB.
    2. Resizes image to expected IMAGE_SIZE (224x224).
    3. Converts image array to float32 normalized to [0, 1].
    4. Expands tensor batch dimensions for Keras inference.
    """
    image = Image.open(image_path).convert("RGB")
    image = image.resize((IMAGE_SIZE, IMAGE_SIZE))
    image = np.array(image).astype("float32")
    image = image / 255.0
    image = np.expand_dims(image, axis=0)
    image = tf.convert_to_tensor(image)
    return image