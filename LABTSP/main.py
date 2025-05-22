from fastapi import FastAPI
from app.api import websocket
from app.core.config import settings
import uvicorn
from app.celery.celery_app import celery_app

app = FastAPI(title=settings.PROJECT_NAME)

# Include WebSocket router
app.include_router(websocket.router, prefix="/ws", tags=["websocket"])

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True) 