from pony.orm import select
from models import WaitingRoom
from fastapi import HTTPException


def validate_unique_room_name(room_name: str) -> bool:
    """
    Checks if the name of the room is valid

    Args:
    creation_request (RoomCreationRequest): Input data to validate

    Returns:
    bool: True if the name is valid, False otherwise
    """
    room_name_exists = select(
        room for room in WaitingRoom if room.room_name == room_name
    ).exists()

    if room_name_exists:
        raise HTTPException(
            status_code=400, detail="Room name already exists"
        )
