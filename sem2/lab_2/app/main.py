from fastapi import FastAPI, WebSocket
from celery import Celery
from app.api import image_processing 
from app.api.endpoints import auth

app = FastAPI()

app.include_router(auth.router)
app.include_router(image_processing.router)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        data = await websocket.receive_text()
        await websocket.send_text(f"Message text was: {data}")

celery = Celery('worker', broker='redis://localhost:6379/0')

@celery.task
def background_task():
    # Долгий процесс
    return "Task completed"