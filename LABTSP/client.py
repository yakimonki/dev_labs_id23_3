import asyncio
import websockets
import json
import click
import sys
from typing import List, Tuple
import getpass

async def connect_and_solve(uri: str, points: List[Tuple[float, float]], token: str):
    async with websockets.connect(f"{uri}?token={token}") as websocket:
        print("Connected to server")
        
        # Send points to solve
        await websocket.send(json.dumps({"points": points}))
        print("Sent points to server")
        
        # Listen for updates
        while True:
            try:
                message = await websocket.recv()
                data = json.loads(message)
                
                if data["status"] == "STARTED":
                    print(f"Task {data['task_id']} started")
                elif data["status"] == "PROGRESS":
                    print(f"Task {data['task_id']} progress: {data['progress']}%")
                elif data["status"] == "COMPLETED":
                    print(f"Task {data['task_id']} completed!")
                    print(f"Path: {data['path']}")
                    print(f"Total distance: {data['total_distance']:.2f}")
                    break
                    
            except websockets.exceptions.ConnectionClosed:
                print("Connection closed")
                break

@click.command()
@click.option('--server', default='ws://localhost:8000/ws', help='WebSocket server URL')
@click.option('--token', prompt=True, hide_input=True, help='Authentication token')
@click.option('--file', type=click.Path(exists=True), help='File containing points (one point per line, format: x y)')
def main(server: str, token: str, file: str):
    """TSP Solver Client"""
    points = []
    
    if file:
        with open(file, 'r') as f:
            for line in f:
                x, y = map(float, line.strip().split())
                points.append((x, y))
    else:
        print("Enter points (one per line, format: x y)")
        print("Press Ctrl+D (Unix) or Ctrl+Z (Windows) when done")
        try:
            while True:
                line = input()
                x, y = map(float, line.strip().split())
                points.append((x, y))
        except EOFError:
            pass
    
    if not points:
        print("No points provided")
        sys.exit(1)
    
    print(f"Solving TSP for {len(points)} points")
    asyncio.run(connect_and_solve(server, points, token))

if __name__ == '__main__':
    main() 