"""Defines 'room' endpoints
"""

from fastapi import APIRouter, status
from schemas.room import RoomCreationRequest, RoomID, PlayerID
from pony.orm import db_session
import services.room_creator as room_creator
from typing import Tuple


room_router = APIRouter()


@room_router.post(path="", status_code=status.HTTP_201_CREATED)
async def create_room(creation_request: RoomCreationRequest) -> Tuple[RoomID, PlayerID]:
    with db_session:
        room_creator.handle_errors(creation_request)
        room = room_creator.create_room_on_db(creation_request)
        player = room_creator.create_host_on_db(room, creation_request)
        response = (RoomID(roomID=room.id), PlayerID(playerID=player.id))

    return response
