from fastapi import WebSocket, WebSocketDisconnect, APIRouter
from lacosa.game.router import play_card  # Importa la función play_card de tu código original

websocket_router = APIRouter()

class GameManager:
    def __init__(self):
        self.active_connections = {}

    async def connect(self, websocket: WebSocket, player_id: int):
        await websocket.accept()
        self.active_connections[player_id] = websocket

    async def disconnect(self, player_id: int):
        if player_id in self.active_connections:
            websocket = self.active_connections[player_id]
            await websocket.close()
            del self.active_connections[player_id]

    async def send_message(self, player_id: int, message: str):
        if player_id in self.active_connections:
            await self.active_connections[player_id].send_text(message)

manager = GameManager()