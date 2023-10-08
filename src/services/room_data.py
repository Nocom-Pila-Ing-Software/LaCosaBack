from fastapi import HTTPException, status
from models import WaitingRoom
from schemas.room import RoomID, PlayerName
from typing import List

def get_number_of_players_in_room(room_id: RoomID) -> int:
    """
    Gets the number of players in a room

    Args:
    room_id (int): The id of the room

    Returns:
    int: The number of players in the room
    """

    room = WaitingRoom[room_id]
    return len(room.players)


def get_players_names_in_room(room_id: RoomID) -> List[PlayerName]:
    """
    Gets the names of the players in a room

    Args:
    room_id (int): The id of the room

    Returns:
    list[PlayerName]: The names of the players in the room
    """

    room = WaitingRoom[room_id]
    players_names = []
    for player in room.players:
        players_names.append(PlayerName(playerName=player.username))
    return players_names


def check_waiting_room_exists(room_ID: int) -> None:
    """
    Verify if the room exists.

    Args:
        room_ID (int): The ID of the room to verify.

    Raises:
        HTTPException: If the room does not exist,
        raise an HTTP exception with a status code of 404.
    """
    if WaitingRoom.get(id=room_ID) is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Room not found"
        )

def has_room_started(room_id: int):
    """
    Check if the room has started.

    Args:
        room_id (int): The ID of the room to verify.
    
    Returns:
        bool: True if the room has started, False otherwise.
    """    

    room = WaitingRoom[room_id]
    return room.game is not None

def check_host_exists(room_ID: int) -> None:
    """
    Verify if the host exists.

    Args:
        room_ID (int): The ID of the room to verify.

    Raises:
        HTTPException: If the host does not exist,
        raise an HTTP exception with a status code of 404.
    """
    room = WaitingRoom[room_ID]
    host = room.players.select(lambda p: p.is_host).first()
    if host is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Host not found"
        )
    