from pydantic import BaseModel
from typing import Dict
from fastapi import WebSocket


class SocketMessage(BaseModel):
    action: str
    data: dict = {}


class SocketConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}

    async def connect(self, identifier: str, websocket: WebSocket):
        await websocket.accept()
        self.active_connections[identifier] = websocket

    def disconnect(self, identifier: str):
        del self.active_connections[identifier]

    def get_connection(self, identifier: str):
        return self.active_connections[identifier]

    async def send_to_participant(self, message: SocketMessage, identifier: str):
        await self.get_connection(identifier).send_text(message.json())

    async def broadcast(self, message: SocketMessage):
        for connection in self.active_connections.values():
            await connection.send_text(message.json())
