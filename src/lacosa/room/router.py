"""
Defines 'room' endpoints
"""
from fastapi import APIRouter, status
from pony.orm import db_session

from lacosa.room.schemas import RoomCreationRequest, RoomCreationResponse, RoomDataResponse, RoomListingList, RoomAddPlayerRequest
from lacosa.room.utils.room_creator import RoomCreator
from lacosa.room.utils.room_data import RoomStatusHandler
from lacosa.room.utils.room_listing import RoomListHandler
from lacosa.room.utils.player_creator import PlayerCreator
from lacosa.room.utils.error_responses import error_responses
from lacosa.room.utils.player_remover import PlayerRemover
from lacosa.schemas import PlayerID

room_router = APIRouter()


@room_router.get(path="/rooms", status_code=status.HTTP_200_OK)
async def get_room_listing() -> RoomListingList:
    """Returns a list of rooms with a summary of their data"""
    with db_session:
        listing_handler = RoomListHandler()
        response = listing_handler.get_response()

    return response


@room_router.get(path="/{room_id}", status_code=status.HTTP_200_OK,
                 responses=error_responses["404"])
async def get_room_info(room_id: int) -> RoomDataResponse:
    """Returns the room data"""
    with db_session:
        status_handler = RoomStatusHandler(room_id)
        response = status_handler.get_response()

    return response


@room_router.post(path="", status_code=status.HTTP_201_CREATED,
                  responses=error_responses["400"])
async def create_room(creation_request: RoomCreationRequest) -> RoomCreationResponse:
    """Creates a new room and returns the room id and the player id"""
    with db_session:
        game_creator = RoomCreator(creation_request)
        game_creator.create()
        response = game_creator.get_response()

    return response


@room_router.post("/{room_id}/player", response_model=PlayerID, status_code=status.HTTP_200_OK,
                  responses=error_responses["400&404"])
async def add_player_to_waiting_room(request_data: RoomAddPlayerRequest, room_id: int) -> PlayerID:
    """Adds a player to the waiting room and returns the player id"""
    with db_session:
        player_creator = PlayerCreator(request_data, room_id)
        player_creator.create()
        response = player_creator.get_response()

        return response


@room_router.delete("/{room_id}/player", status_code=status.HTTP_200_OK,
                    responses=error_responses["400&404"])
async def remove_player_from_room(request_data: PlayerID, room_id: int) -> None:
    """Removes a player from a waiting room

    If the player is the host, the room is deleted
    """
    with db_session:
        game_creator = PlayerRemover(request_data, room_id)
        game_creator.execute_action()
