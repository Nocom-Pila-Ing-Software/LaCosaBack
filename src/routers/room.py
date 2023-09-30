from fastapi import APIRouter, status
from schemas.player import PlayerID, PlayerName
from pony.orm import db_session
from models import WaitingRoom
import services.room_operations as room_ops

room_router = APIRouter()

@room_router.post("/{roomID}/players", response_model=PlayerID, status_code=status.HTTP_200_OK)
async def add_player_to_waiting_room(request_data: PlayerName, roomID: int) -> PlayerID:
    with db_session:
        player_name = request_data.playerName
        room_ops.check_valid_player_name(player_name)
        room_ops.check_waiting_room_exists(roomID)
        room = WaitingRoom.get(id=roomID)
        player = room_ops.create_player(player_name, room)
        room_ops.check_player_exists_in_database(player)
        room.players.add(player)
        room_ops.is_player_added_to_room(player, room)

        response = PlayerID(playerID=player.id)

        return response