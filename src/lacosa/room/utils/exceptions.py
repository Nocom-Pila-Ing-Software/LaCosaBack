from pony.orm import select
from models import WaitingRoom, Player
from fastapi import HTTPException, status


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


def check_valid_player_name(player_name: str) -> None:
    """
    Validate that the player's name is not empty.

    Args:
        player_name (PlayerName): The player's name.

    Raises:
        HTTPException: If the player's name is empty, raise an HTTP exception with a status code of 400.
    """
    if not player_name:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Player name cannot be empty"
        )


def check_player_name_is_unique(player_name: str, room: WaitingRoom) -> None:
    """
    Verify if the player's name is unique in the room.

    Args:
        player_name (PlayerName): The player's name.
        room_ID (int): The ID of the room in which to verify the player's name.

    Raises:
        HTTPException: If the player's name is not unique, raise an HTTP exception with a status code of 400.
    """
    # check if there's more than one player with the same name in the room
    player_name_is_unique = room.players.filter(
        lambda player: player.username == player_name
    ).count() == 0

    if not player_name_is_unique:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Player name already exists in room"
        )


def check_game_started(room: WaitingRoom) -> None:
    """
    Verify if the game has started.

    Args:
        room_ID (int): The ID of the room in which to verify if the game has started.

    Raises:
        HTTPException: If the game has started, raise an HTTP exception with a status code of 400.
    """
    if room.game is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Game has already started"
        )
