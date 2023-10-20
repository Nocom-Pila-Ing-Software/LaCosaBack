"""
Defines 'room' endpoints
"""

from fastapi import APIRouter, status
from pony.orm import db_session
from lacosa.room.schemas import RoomCreationRequest, RoomCreationResponse, RoomDataResponse, RoomListingList, RoomAddPlayerRequest
from lacosa.room.utils.room_creator import RoomCreator
from lacosa.room.utils.room_data import RoomStatusHandler
from lacosa.room.utils.player_creator import PlayerCreator
from lacosa.schemas import PlayerName, PlayerID

room_router = APIRouter()


@room_router.get(path="/rooms", status_code=status.HTTP_200_OK)
async def get_room_listing() -> RoomListingList:
    """Returns a list of rooms with a summary of their data"""
    with db_session:
        pass


@room_router.get(path="/{room_id}", status_code=status.HTTP_200_OK)
async def get_room_info(room_id: int) -> RoomDataResponse:
    """Returns the room data"""
    with db_session:
        status_handler = RoomStatusHandler(room_id)
        response = status_handler.get_response()

    return response


@room_router.post(path="", status_code=status.HTTP_201_CREATED)
async def create_room(creation_request: RoomCreationRequest) -> RoomCreationResponse:
    """Creates a new room and returns the room id and the player id

    The password is optional
    """
    with db_session:
        game_creator = RoomCreator(creation_request)
        game_creator.create()
        response = game_creator.get_response()

    return response


@room_router.post("/{room_id}/player", response_model=PlayerID, status_code=status.HTTP_200_OK)
async def add_player_to_waiting_room(request_data: RoomAddPlayerRequest) -> PlayerID:
    """Adds a player to the waiting room and returns the player id"""
    with db_session:
        player_creator = PlayerCreator(request_data)
        player_creator.create()
        response = player_creator.get_response()

        return response


@room_router.delete("/{room_id}/leave", status_code=status.HTTP_200_OK)
async def leave_room(player_id: int) -> None:
    """Removes a player from a waiting room

    If the player is the host, the room is deleted
    """
    with db_session:
        pass
