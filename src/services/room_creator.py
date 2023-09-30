from fastapi import HTTPException
from pony.orm import select
from models import WaitingRoom
from schemas.room import RoomCreationRequest


def create_host_on_db(room: WaitingRoom) -> int:
    """
    Creates a new host for a room on the database

    Args:
    room (WaitingRoom): The room to create the host for

    Returns:
    int: The id of the new host
    """
    new_host = room.players.create(
        username=RoomCreationRequest.hostName,
        is_host=True
    )
    return new_host.id


def create_room_on_db(creation_request: RoomCreationRequest) -> WaitingRoom:
    """
    Creates a new room on the database

    Args:
    creation_request (RoomCreationRequest): Input data to validate

    Returns:
    WaitingRoom: The created room
    """
    new_room = WaitingRoom(
        name=creation_request.roomName
    )
    return new_room


def valid_name(creation_request: RoomCreationRequest) -> bool:
    """
    Checks if the name of the room is valid

    Args:
    creation_request (RoomCreationRequest): Input data to validate

    Returns:
    bool: True if the name is valid, False otherwise
    """
    return not select(
        room for room in WaitingRoom if room.name == creation_request.roomName
    ).exists()


def handle_errors(creation_request: RoomCreationRequest) -> None:
    """
    Checks for errors in creation_request and raises HTTPException if needed

    Args:
    creation_request (RoomCreationRequest): Input data to validate

    Raises:
    HTTPException(status_code=400): If the characteristics of the room are invalid
    """
    if not valid_name(creation_request):
        raise HTTPException(
            status_code=404, detail="Room name already exists"
        )
