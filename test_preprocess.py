from app.ai.preprocess import preprocess_image

img = preprocess_image("sample0.jpg")
img5 = preprocess_image("sample5.jpg")

print(img.shape)
print(img5.shape)


