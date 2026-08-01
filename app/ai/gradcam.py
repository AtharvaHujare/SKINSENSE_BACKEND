import os
import cv2
import numpy as np
import tensorflow as tf
from PIL import Image

from app.ai.model_loader import load_model
from app.ai.preprocess import preprocess_image

LAST_CONV_LAYER = "top_conv"

OUTPUT_DIR = "outputs"

os.makedirs(OUTPUT_DIR, exist_ok=True)


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

    print("Gradient min:", tf.reduce_min(grads).numpy())
    print("Gradient max:", tf.reduce_max(grads).numpy())
    print("Gradient mean:", tf.reduce_mean(grads).numpy())

    pooled_grads = tf.reduce_mean(grads, axis=(0, 1, 2))

    conv_output = conv_output[0]

    heatmap = tf.reduce_sum(conv_output * pooled_grads, axis=-1)

    print("Heatmap before ReLU:")
    print(heatmap.numpy())

    heatmap = tf.maximum(heatmap, 0)

    heatmap /= (tf.reduce_max(heatmap) + 1e-8)

    heatmap = heatmap.numpy()

    heatmap_uint8 = np.uint8(255 * heatmap)
    success = cv2.imwrite("outputs/raw_heatmap.jpg", heatmap_uint8)
    print("Raw heatmap saved:", success)

    # -------------------------
    # Overlay Heatmap
    # -------------------------

    

    original = Image.open(image_path).convert("RGB")

    original = np.array(original)

    # Convert RGB -> BGR for OpenCV
    original = cv2.cvtColor(original, cv2.COLOR_RGB2BGR)

    heatmap = cv2.resize(
        heatmap,
        (original.shape[1], original.shape[0])
    )

    heatmap = np.uint8(255 * heatmap)

    heatmap = cv2.applyColorMap(
        heatmap,
        cv2.COLORMAP_JET
    )

    overlay = cv2.addWeighted(
        original,
        0.8,
        heatmap,
        0.2,
        0
    )

    filename = os.path.basename(image_path)

    output_path = os.path.join(
        OUTPUT_DIR,
        f"gradcam_{filename}"
    )

    cv2.imwrite(output_path, overlay)

    return output_path