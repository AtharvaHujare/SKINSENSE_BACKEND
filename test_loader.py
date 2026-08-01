from app.ai.model_loader import load_model

model = load_model()

print("Model loaded successfully!")
print(model.input_shape)
print(model.output_shape)