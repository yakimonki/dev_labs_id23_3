# app/api/image_processing.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import base64
import numpy as np
from PIL import Image
import io
import cv2

router = APIRouter()

class ImageRequest(BaseModel):
    image_base64: str  # Строка base64 с изображением

def otsu_binarization(image_array: np.ndarray) -> bytes:
    """
    Применяет алгоритм Отсу к изображению.
    Возвращает бинаризованное изображение в формате base64.
    """
    # Конвертация в grayscale, если нужно
    if len(image_array.shape) == 3:
        image_array = cv2.cvtColor(image_array, cv2.COLOR_RGB2GRAY)
    
    # Применение алгоритма Отсу
    _, binary_image = cv2.threshold(
        image_array, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU
    )
    
    # Конвертация в байты
    _, buffer = cv2.imencode('.png', binary_image)
    return base64.b64encode(buffer).decode('utf-8')

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