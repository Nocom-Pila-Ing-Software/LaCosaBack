from fastapi import HTTPException, status
from player.schemas import PlayerName
from pony.orm import db_session, commit, select
from models import WaitingRoom, Player

def create_player(player_name: PlayerName, room: WaitingRoom) -> Player:
    """
    Create a new player and add them to the database.

    Args:
        player_name (PlayerName): The player's name.
        room_ID (int): The ID of the room to which the player will be added.

    Returns:
        Player: The created player.
    """

    #count players in room ERROR
    player_count = len(room.players)
    room_ID = room.id

    player = Player(username=player_name, room=room_ID, position=player_count+1)
    commit()

    return player



def check_valid_player_name(player_name: PlayerName) -> None:
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

def check_player_exists_in_database(player: Player) -> None:
    """
    Verify if the player has been successfully created in the database.

    Args:
        player (Player): The player to verify.

    Raises:
        HTTPException: If the player has not been created successfully, raise an HTTP exception with a status code of 400.
    """
    if player is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Player not created"
        )

def check_waiting_room_exists(room_ID: int) -> None:
    """
    Verify if the room exists.

    Args:
        room_ID (int): The ID of the room to verify.

    Raises:
        HTTPException: If the room does not exist, raise an HTTP exception with a status code of 404.
    """
    if WaitingRoom.get(id=room_ID) is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Room not found"
        )

def is_player_added_to_room(player: Player, room: WaitingRoom) -> None:
    """
    Verify if a player has been added to a room.

    Args:
        player (Player): The player to verify.
        room (WaitingRoom): The room in which to check the existence of the player.

    Raises:
        HTTPException: If the player has not been added to the room, raise an HTTP exception with a status code of 400.
    """
    if player not in room.players:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Player not added to room"
        )

def check_player_name_is_unique(player_name: PlayerName, room_ID: int) -> None:
    """
    Verify if the player's name is unique in the room.

    Args:
        player_name (PlayerName): The player's name.
        room_ID (int): The ID of the room in which to verify the player's name.

    Raises:
        HTTPException: If the player's name is not unique, raise an HTTP exception with a status code of 400.
    """
    if select(p for p in Player if p.username == player_name and p.room.id == room_ID).get() is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Player name already exists in room"
        )

def check_game_started(room_ID: int) -> None:
    """
    Verify if the game has started.

    Args:
        room_ID (int): The ID of the room in which to verify if the game has started.

    Raises:
        HTTPException: If the game has started, raise an HTTP exception with a status code of 400.
    """
    if WaitingRoom.get(id=room_ID).game is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Game has already started"
        )
    
def delete_room(room_ID: int) -> None:
    """
    Delete a room from the database.

    Args:
        room_ID (int): The ID of the room to delete.
    """
    WaitingRoom[room_ID].delete()
    commit()