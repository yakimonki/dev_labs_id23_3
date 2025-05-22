from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, HTTPException
from app.websocket.manager import manager
from app.celery.tasks import solve_tsp
from typing import List, Tuple
from app.core.auth import get_current_user_ws
from app.models.user import User

router = APIRouter()

@router.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str):
    try:
        # Authenticate user
        user = await get_current_user_ws(websocket)
        if str(user.id) != user_id:
            await websocket.close(code=4001)
            return

        await manager.connect(websocket, user_id)
        try:
            while True:
                data = await websocket.receive_json()
                
                if "points" in data:
                    points: List[Tuple[float, float]] = data["points"]
                    
                    # Start TSP solving task
                    task = solve_tsp.delay(points, user_id)
                    
                    # Send initial status
                    await manager.send_task_started(user_id, task.id)
                    
        except WebSocketDisconnect:
            manager.disconnect(websocket, user_id)
            
    except HTTPException:
        await websocket.close(code=4001)
    except Exception as e:
        await websocket.close(code=4000) 