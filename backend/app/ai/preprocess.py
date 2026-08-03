import json
from pathlib import Path

import numpy as np
import tensorflow as tf
from PIL import Image


BASE_DIR = Path(__file__).resolve().parent

CONFIG_PATH = BASE_DIR / "models" / "config.json"


with open(CONFIG_PATH) as f:
    CONFIG = json.load(f)


IMAGE_SIZE = CONFIG["image_size"]


def preprocess_image(image_path):

    image = Image.open(image_path).convert("RGB")

    image = image.resize(
        (IMAGE_SIZE, IMAGE_SIZE)
    )

    image = np.array(image).astype("float32")

    image = image / 255.0

    image = np.expand_dims(
        image,
        axis=0
    )

    image = tf.convert_to_tensor(image)

    return image