import requests
import base64

# Загружаем изображение
with open("image-asset.jpeg", "rb") as f:
    image_base64 = base64.b64encode(f.read()).decode("utf-8")

# Отправляем запрос
response = requests.post(
    "http://localhost:8000/binary_image",
    json={"image_base64": image_base64}
)

# Сохраняем результат
binary_image = base64.b64decode(response.json()["binary_image"])
with open("binary_result.png", "wb") as f:
    f.write(binary_image)