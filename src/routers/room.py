"""Defines 'room' endpoints
"""

from fastapi import APIRouter, status
from schemas.room import RoomCreationRequest, RoomID, PlayerID
from pony.orm import db_session
import services.room_creator as room_creator

room_router = APIRouter()


@room_router.post(path="", status_code=status.HTTP_201_CREATED)
async def create_room(creation_request: RoomCreationRequest) -> (RoomID, PlayerID):
    with db_session:
        room_creator.handle_errors(creation_request)
        room = room_creator.create_room_on_db(creation_request)
        player_id = room_creator.create_host_on_db(room)
        response = (RoomID(roomID=room.id), PlayerID(playerID=player_id))

    return response
