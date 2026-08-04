import json
import logging
import numpy as np
from pathlib import Path

from app.ai.preprocess import preprocess_image
from app.ai.model_loader import load_model
from app.ai.gradcam import generate_gradcam

logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parent
CLASS_NAMES_PATH = BASE_DIR / "models" / "class_names.json"

DEFAULT_CLASS_NAMES = ["akiec", "bcc", "bkl", "df", "mel", "nv", "vasc"]

if CLASS_NAMES_PATH.exists():
    try:
        with open(CLASS_NAMES_PATH, "r", encoding="utf-8") as f:
            CLASS_NAMES = json.load(f)
    except Exception as exc:
        logger.warning("Could not read class_names.json at '%s': %s", CLASS_NAMES_PATH, exc)
        CLASS_NAMES = DEFAULT_CLASS_NAMES
else:
    CLASS_NAMES = DEFAULT_CLASS_NAMES


def predict(image_path: str):
    """
    Predicts the skin disease classification from an image filepath.

    Returns:
    {
        "prediction": disease_class,
        "confidence": float,
        "risk_level": "High" | "Low",
        "heatmap_path": gradcam_path
    }
    """
    image = preprocess_image(image_path)
    model = load_model()

    prediction = model.predict(image, verbose=0)

    logger.info("Raw prediction tensor shape: %s", prediction.shape)

    predicted_index = int(np.argmax(prediction[0]))
    confidence = float(prediction[0][predicted_index]) * 100

    if predicted_index < len(CLASS_NAMES):
        disease = CLASS_NAMES[predicted_index]
    else:
        disease = "unknown"

    HIGH_RISK = ["mel", "bcc", "akiec"]
    risk = "High" if disease in HIGH_RISK else "Low"

    try:
        heatmap_path = generate_gradcam(image_path)
    except Exception as exc:
        logger.warning("Grad-CAM generation encountered an issue: %s", exc)
        heatmap_path = None

    return {
        "prediction": disease,
        "confidence": round(confidence, 2),
        "risk_level": risk,
        "heatmap_path": heatmap_path
    }