import json
import numpy as np

from app.ai.preprocess import preprocess_image
from app.ai.model_loader import load_model
from app.ai.gradcam import generate_gradcam
# Load class names once
with open("models/class_names.json", "r") as f:
    CLASS_NAMES = json.load(f)


def predict(image_path: str):
    """
    Predict the skin disease from an image.

    Returns:
    {
        prediction,
        confidence,
        risk
    }
    """

    image = preprocess_image(image_path)

    model = load_model()
    prediction = model.predict(image, verbose=0)

    print("Raw prediction:", prediction)


    print("Probabilities:", prediction[0])

    predicted_index = np.argmax(prediction)

    confidence = float(prediction[0][predicted_index])

    disease = CLASS_NAMES[predicted_index]

    HIGH_RISK = ["mel", "bcc", "akiec"]

    risk = "High" if disease in HIGH_RISK else "Low"
    heatmap_path = generate_gradcam(image_path)
    return {
    "prediction": disease,
    "confidence": round(confidence, 4),
    "risk": risk,
    "heatmap_path": heatmap_path
}