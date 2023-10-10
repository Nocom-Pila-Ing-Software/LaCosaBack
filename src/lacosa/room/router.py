"""
Defines 'room' endpoints
"""

from fastapi import APIRouter, status
from pony.orm import db_session
from lacosa.room.schemas import RoomCreationRequest, RoomCreationResponse, RoomDataResponse
import lacosa.room.utils.room_creator as room_creator
import lacosa.room.utils.room_data as room_data
import lacosa.room.utils.room_operations as room_ops
from lacosa.player.schemas import PlayerName, PlayerID
from models import WaitingRoom

room_router = APIRouter()


@room_router.post(path="", status_code=status.HTTP_201_CREATED)
async def create_room(creation_request: RoomCreationRequest) -> RoomCreationResponse:
    with db_session:
        room_creator.handle_errors(creation_request)
        room = room_creator.create_room_on_db(creation_request)
        player = room_creator.create_host_on_db(room, creation_request)
        response = RoomCreationResponse(
            roomID=room.id,
            playerID=player.id
        )

    return response


@room_router.get(path="/{room_id}", status_code=status.HTTP_200_OK)
async def get_room_info(room_id: int) -> RoomDataResponse:
    with db_session:
        room_data.check_waiting_room_exists(room_id)
        number_players = room_data.get_number_of_players_in_room(room_id)
        players_names_room = room_data.get_players_names_in_room(room_id)
        has_room_started = room_data.has_room_started(room_id)
        response = RoomDataResponse(
            CountPlayers=number_players,
            Players=players_names_room,
            hasStarted=has_room_started
        )

    return response


@room_router.post("/{room_id}/players", response_model=PlayerID, status_code=status.HTTP_200_OK)
async def add_player_to_waiting_room(request_data: PlayerName, room_id: int) -> PlayerID:
    with db_session:
        player_name = request_data.playerName
        room_ops.check_valid_player_name(player_name)
        room_ops.check_waiting_room_exists(room_id)
        room_data.check_host_exists(room_id)
        room_ops.check_player_name_is_unique(player_name, room_id)
        room_ops.check_game_started(room_id)
        room = WaitingRoom.get(id=room_id)
        player = room_ops.create_player(player_name, room)
        room_ops.check_player_exists_in_database(player)
        room.players.add(player)
        room_ops.is_player_added_to_room(player, room)

        response = PlayerID(playerID=player.id)

        return response
