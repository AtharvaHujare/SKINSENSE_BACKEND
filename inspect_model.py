from app.ai.model_loader import load_model

model = load_model()

base_model = model.get_layer("efficientnetb0")

for layer in base_model.layers[-20:]:
    print(layer.name)