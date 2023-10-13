"""
Defines 'room' endpoints
"""

from fastapi import APIRouter, status
from pony.orm import db_session
from lacosa.room.schemas import RoomCreationRequest, RoomCreationResponse, RoomDataResponse
from lacosa.room.utils.room_creator import RoomCreator
from lacosa.room.utils.room_data import RoomStatusHandler
from lacosa.room.utils.room_operations import PlayerCreator
from schemas.schemas import PlayerName, PlayerID

room_router = APIRouter()


@room_router.post(path="", status_code=status.HTTP_201_CREATED)
async def create_room(creation_request: RoomCreationRequest) -> RoomCreationResponse:
    with db_session:
        game_creator = RoomCreator(creation_request)
        game_creator.create()
        response = game_creator.get_response()

    return response


@room_router.get(path="/{room_id}", status_code=status.HTTP_200_OK)
async def get_room_info(room_id: int) -> RoomDataResponse:
    with db_session:
        status_handler = RoomStatusHandler(room_id)
        response = status_handler.get_response()

    return response


@room_router.post("/{room_id}/players", response_model=PlayerID, status_code=status.HTTP_200_OK)
async def add_player_to_waiting_room(request_data: PlayerName, room_id: int) -> PlayerID:
    with db_session:
        game_creator = PlayerCreator(request_data, room_id)
        game_creator.create()
        response = game_creator.get_response()

        return response
