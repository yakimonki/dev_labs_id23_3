from typing import Dict, Set
from fastapi import WebSocket
import json

class WebSocketManager:
    def __init__(self):
        self.active_connections: Dict[str, Set[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, user_id: str):
        await websocket.accept()
        if user_id not in self.active_connections:
            self.active_connections[user_id] = set()
        self.active_connections[user_id].add(websocket)

    def disconnect(self, websocket: WebSocket, user_id: str):
        if user_id in self.active_connections:
            self.active_connections[user_id].remove(websocket)
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]

    async def send_task_started(self, user_id: str, task_id: str):
        if user_id in self.active_connections:
            message = {
                "status": "STARTED",
                "task_id": task_id,
                "message": "Задача запущена"
            }
            for connection in self.active_connections[user_id]:
                await connection.send_json(message)

    async def send_task_progress(self, user_id: str, task_id: str, progress: int):
        if user_id in self.active_connections:
            message = {
                "status": "PROGRESS",
                "task_id": task_id,
                "progress": progress
            }
            for connection in self.active_connections[user_id]:
                await connection.send_json(message)

    async def send_task_completed(self, user_id: str, task_id: str, path: list, total_distance: float):
        if user_id in self.active_connections:
            message = {
                "status": "COMPLETED",
                "task_id": task_id,
                "path": path,
                "total_distance": total_distance
            }
            for connection in self.active_connections[user_id]:
                await connection.send_json(message)

manager = WebSocketManager() 