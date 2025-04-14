import base64
import subprocess
import json

# Открытие изображения в бинарном режиме
with open(r"C:\Users\nasty\Practicum_2kurs\ImageBinarization\random.jpg", "rb") as image_file:
    encoded_image = base64.b64encode(image_file.read()).decode("utf-8")

json_data = json.dumps(encoded_image)
print(json_data) 