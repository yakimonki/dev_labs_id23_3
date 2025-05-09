from fastapi import FastAPI, HTTPException, APIRouter
from pydantic import BaseModel
import base64
import numpy as np
from PIL import Image
import io
import cv2
from typing import Optional, Literal
import logging

# Создаем объект FastAPI
app = FastAPI()

# Создаем APIRouter для обработки запросов
router = APIRouter()

# Настройка логгера
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Модели запросов и ответов
class ImageRequest(BaseModel):
    image: str  # Строка base64 с изображением
    algorithm: Literal["otsu"] = "otsu"  # Доступные алгоритмы
    threshold: Optional[int] = None  # Порог для простой бинаризации

class ImageResponse(BaseModel):
    binarized_image: str
    algorithm_used: str
    original_size: tuple[int, int]
    processed_size: tuple[int, int]
    processing_time_ms: float

# Вспомогательные функции
def validate_image_size(image_array: np.ndarray):
    """Проверяет размер изображения"""
    max_size = 5000  # Максимальный размер по любой стороне
    if max(image_array.shape) > max_size:
        raise ValueError(f"Изображение слишком большое. Максимальный размер: {max_size}x{max_size}")

def image_to_base64(image_array: np.ndarray) -> str:
    """Конвертирует numpy array в base64 строку (PNG)"""
    success, buffer = cv2.imencode('.png', image_array)
    if not success:
        raise ValueError("Ошибка кодирования изображения в PNG")
    return base64.b64encode(buffer).decode('utf-8')

def base64_to_image(base64_str: str) -> np.ndarray:
    """Конвертирует base64 строку в numpy array"""
    try:
        image_bytes = base64.b64decode(base64_str)
        image = Image.open(io.BytesIO(image_bytes))
        return np.array(image)
    except Exception as e:
        raise ValueError(f"Ошибка декодирования base64: {str(e)}")

# Алгоритмы бинаризации
def apply_otsu(image_array: np.ndarray) -> np.ndarray:
    """Реализация алгоритма Отсу для бинаризации изображения без использования cv2.THRESH_OTSU"""
    if len(image_array.shape) == 3:
        image_array = cv2.cvtColor(image_array, cv2.COLOR_RGB2GRAY)
    
    pixel_values = image_array.flatten()
    hist, bin_edges = np.histogram(pixel_values, bins=256, range=(0, 255))
    total_pixels = image_array.size
    prob = hist / total_pixels
    cumsum = np.cumsum(prob)
    cumulative_mean = np.cumsum(prob * np.arange(256))

    max_between_class_variance = 0
    best_threshold = 0

    for t in range(1, 256):
        p1 = cumsum[t]
        p2 = 1 - p1
        mean1 = cumulative_mean[t] / p1 if p1 > 0 else 0
        mean2 = (cumulative_mean[-1] - cumulative_mean[t]) / p2 if p2 > 0 else 0
        between_class_variance = p1 * p2 * (mean1 - mean2) ** 2

        if between_class_variance > max_between_class_variance:
            max_between_class_variance = between_class_variance
            best_threshold = t

    _, binary_image = cv2.threshold(image_array, best_threshold, 255, cv2.THRESH_BINARY)
    return binary_image

# Основной эндпоинт для обработки изображения
@router.post("/binary_image")
async def binary_image(request: ImageRequest):
    try:
        # Декодируем изображение из base64 в numpy array
        image_array = base64_to_image(request.image)

        # Применяем выбранный алгоритм
        if request.algorithm == "otsu":
            processed_image = apply_otsu(image_array)
        else:
            raise HTTPException(status_code=400, detail="Неподдерживаемый алгоритм")

        # Преобразуем обработанное изображение обратно в base64
        binarized_image_base64 = image_to_base64(processed_image)
        with open(r"C:\Users\nasty\Practicum_2kurs\ImageBinarization\binarized_image.txt", 'w') as f:
            f.write(binarized_image_base64)
        return {"binarized_image": binarized_image_base64}
    except Exception as e:
        raise HTTPException(status_code=500, detail="Произошла ошибка на сервере")

# Регистрация роутера в приложении FastAPI
app.include_router(router)
