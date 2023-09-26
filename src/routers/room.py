
from fastapi import APIRouter, HTTPException, status
from schemas.room import PlayerID
from pony.orm import db_session
from models import WaitingRoom, Player

room_router = APIRouter()

@room_router.post("/room/player", status_code=status.HTTP_200_OK)
async def add_player_to_waiting_room(player_id: int, room_id: int) -> PlayerID:
    with db_session:
        # Verificar si la ID del jugador es válida
        player = Player.get(id=player_id)
        if not player:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid player ID")

        # Buscar la sala de espera por su ID
        waiting_room = WaitingRoom.get(id=room_id)
        if not waiting_room:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Waiting room not found")

        # Agregar el jugador a la sala de espera
        waiting_room.players.add(player)

        # Retornar el ID del jugador
        response = PlayerID(playerID=player_id)

        return response
