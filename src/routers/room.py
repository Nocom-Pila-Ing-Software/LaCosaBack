"""
Defines 'room' endpoints
"""

from fastapi import APIRouter, status
from schemas.room import RoomCreationRequest, RoomCreationResponse, RoomDataResponse
from pony.orm import db_session
import services.room_creator as room_creator
import services.room_data as room_data
from schemas.player import PlayerName, PlayerID
import services.room_operations as room_ops
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
        response = RoomDataResponse(
            CountPlayers=number_players,
            Players=players_names_room
        )

    return response


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
