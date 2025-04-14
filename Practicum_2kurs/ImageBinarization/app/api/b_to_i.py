import base64
import io
from PIL import Image
import os
from pathlib import Path

def base64_to_image(base64_string, output_file):
    """
    Декодирует строку Base64 в изображение и сохраняет его в файл.
    
    :param base64_string: Строка Base64 с данными изображения
    :param output_file: Путь для сохранения изображения
    """
    try:
        # Удаляем возможный префикс (например, 'data:image/png;base64,')
        if ',' in base64_string:
            base64_string = base64_string.split(',')[1]
        
        # Добавляем padding, если необходимо
        padding = len(base64_string) % 4
        if padding:
            base64_string += '=' * (4 - padding)
        
        # Декодируем Base64
        image_data = base64.b64decode(base64_string)
        
        # Создаем изображение из бинарных данных
        image = Image.open(io.BytesIO(image_data))
        
        # Сохраняем изображение
        image.save(output_file)
        print(f"Изображение успешно сохранено как {output_file}")
        return True
    except Exception as e:
        print(f"Ошибка при декодировании Base64: {str(e)}")
        return False

# Пример использования
if __name__ == "__main__":

    PROJECT_ROOT = Path(__file__).parent.parent.parent  # Поднимаемся на 3 уровня вверх из /app/api
    BINARIZED_IMAGE_PATH = PROJECT_ROOT / 'binarized_image.txt'

    with open(BINARIZED_IMAGE_PATH, 'r') as f:
        content = f.read()
    
    # Путь для сохранения (используйте raw-строку или двойные обратные слеши)
    output_path = r"C:\Users\nasty\Practicum_2kurs\ImageBinarization\output.png"
    
    base64_to_image(content, output_path)