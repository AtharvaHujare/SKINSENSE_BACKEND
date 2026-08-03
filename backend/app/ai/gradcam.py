import os
from pathlib import Path

import cv2
import numpy as np
import tensorflow as tf
from PIL import Image

from app.ai.model_loader import load_model
from app.ai.preprocess import preprocess_image


BASE_DIR = Path(__file__).resolve().parent

OUTPUT_DIR = BASE_DIR / "outputs"
OUTPUT_DIR.mkdir(exist_ok=True)


LAST_CONV_LAYER = "top_conv"


def generate_gradcam(image_path):

    model = load_model()

    base_model = model.get_layer("efficientnetb0")

    last_conv_layer = base_model.get_layer(LAST_CONV_LAYER)

    conv_model = tf.keras.Model(
        base_model.input,
        last_conv_layer.output
    )

    img = preprocess_image(image_path)

    x = model.get_layer("data_augmentation")(img, training=False)

    with tf.GradientTape() as tape:

        conv_output = conv_model(x)

        y = conv_output

        passed = False

        for layer in model.layers:

            if layer.name == "efficientnetb0":
                passed = True
                continue

            if passed:
                y = layer(y)

        predictions = y

        pred_index = tf.argmax(predictions[0])

        loss = predictions[:, pred_index]


    grads = tape.gradient(loss, conv_output)

    pooled_grads = tf.reduce_mean(
        grads,
        axis=(0, 1, 2)
    )

    conv_output = conv_output[0]

    heatmap = tf.reduce_sum(
        conv_output * pooled_grads,
        axis=-1
    )

    heatmap = tf.maximum(heatmap, 0)

    heatmap /= (
        tf.reduce_max(heatmap)
        + 1e-8
    )

    heatmap = heatmap.numpy()


    original = Image.open(image_path).convert("RGB")
    original = np.array(original)

    original = cv2.cvtColor(
        original,
        cv2.COLOR_RGB2BGR
    )


    heatmap = cv2.resize(
        heatmap,
        (original.shape[1], original.shape[0])
    )

    heatmap = np.uint8(
        255 * heatmap
    )

    heatmap_color = cv2.applyColorMap(
        heatmap,
        cv2.COLORMAP_JET
    )


    overlay = cv2.addWeighted(
        original,
        0.8,
        heatmap_color,
        0.2,
        0
    )


    filename = os.path.basename(image_path)

    output_path = OUTPUT_DIR / f"gradcam_{filename}"

    cv2.imwrite(
        str(output_path),
        overlay
    )

    return str(output_path)