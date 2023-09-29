from fastapi import APIRouter, HTTPException, status
from schemas.player import PlayerID, PlayerName
from pony.orm import db_session
from models import WaitingRoom, Player
from services.room_operations import *

room_router = APIRouter()

@room_router.post("/{roomID}/players", response_model=PlayerID, status_code=status.HTTP_200_OK)
async def add_player_to_waiting_room(request_data: PlayerName, roomID: int) -> PlayerID:
    with db_session:
        # Obtener el playerName del cuerpo de la solicitud
        player_name = request_data.playerName
        # Verificar que el playerName no esté vacío
        player_name_valid(player_name)
        # Verificar que la sala exista
        waiting_room_exists(roomID)
        # Obtener el roomID de la ruta
        room = WaitingRoom.get(id=roomID)
        # Crear un nuevo jugador
        player = create_player(player_name, room)
        # Verificar que el jugador se creó correctamente
        player_exists_in_database(player)
        # Agregar jugador a la sala
        room.players.add(player)
        # Verificar que el jugador se agregó correctamente a la sala
        player_added_to_room(player, room)

        # Retornar el ID del jugador
        response = PlayerID(playerID=player.id)

        return response