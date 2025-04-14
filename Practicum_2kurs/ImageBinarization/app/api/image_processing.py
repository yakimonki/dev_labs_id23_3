# app/api/image_processing.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import base64
import numpy as np
from PIL import Image
import io
import math

router = APIRouter()

class ImageRequest(BaseModel):
    image_base64: str  # Строка base64 с изображением

def otsu_binarization(image_array: np.ndarray) -> bytes:
    """
    Реализация алгоритма Отсу для бинаризации изображения
    без использования OpenCV.
    Возвращает бинаризованное изображение в формате base64.
    """
    # Конвертация в grayscale, если нужно
    if len(image_array.shape) == 3:
        image_array = np.dot(image_array[..., :3], [0.2989, 0.5870, 0.1140])
    
    # Нормализация значений пикселей в диапазон 0-255
    image_array = image_array.astype(np.uint8)
    
    # Вычисление гистограммы
    hist = np.histogram(image_array, bins=256, range=(0, 255))[0]
    
    # Нормализация гистограммы
    hist_norm = hist.astype(np.float32) / hist.sum()
    
    # Вычисление кумулятивных сумм и средних
    cum_sum = np.cumsum(hist_norm)
    cum_mean = np.cumsum(hist_norm * np.arange(256))
    
    # Общее среднее значение
    global_mean = cum_mean[-1]
    
    # Вычисление межклассовой дисперсии
    max_variance = 0
    optimal_threshold = 0
    
    for t in range(1, 256):
        w0 = cum_sum[t]
        w1 = 1 - w0
        
        if w0 == 0 or w1 == 0:
            continue
            
        mean0 = cum_mean[t] / w0
        mean1 = (global_mean - cum_mean[t]) / w1
        
        between_variance = w0 * w1 * (mean0 - mean1) ** 2
        
        if between_variance > max_variance:
            max_variance = between_variance
            optimal_threshold = t
    
    # Применение порога
    binary_image = np.where(image_array > optimal_threshold, 255, 0).astype(np.uint8)
    
    # Конвертация в байты через PIL
    img = Image.fromarray(binary_image)
    byte_arr = io.BytesIO()
    img.save(byte_arr, format='PNG')
    return base64.b64encode(byte_arr.getvalue()).decode('utf-8')

@router.post("/binary_image")
async def binary_image(image_data: ImageRequest):
    try:
        # Декодируем base64
        image_bytes = base64.b64decode(image_data.image_base64)
        image = Image.open(io.BytesIO(image_bytes))
        
        # Конвертация в numpy array
        image_array = np.array(image)
        
        # Применяем бинаризацию
        result_base64 = otsu_binarization(image_array)
        
        return {"binary_image": result_base64}
    
    except Exception as e:
        raise HTTPException(
            status_code=400, 
            detail=f"Ошибка обработки изображения: {str(e)}"
        )