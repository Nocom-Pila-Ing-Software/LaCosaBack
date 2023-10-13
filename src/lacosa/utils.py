from pony.orm import select
from models import Game, Player, Card, WaitingRoom
from fastapi import HTTPException, status


def find_room(room_id: int, failure_status=status.HTTP_404_NOT_FOUND) -> Game:
    room = select(r for r in WaitingRoom if r.id == room_id).get()
    if room is None:
        raise HTTPException(
            status_code=failure_status, detail="Room not found")
    return room


def find_game(game_id: int, failure_status=status.HTTP_404_NOT_FOUND) -> Game:
    """
    Find a game by ID

    Args:
    game_id (int): The ID of the game to find

    Returns:
    Game: The game with the given ID
    """

    game = select(g for g in Game if g.id == game_id).get()
    if game is None:
        raise HTTPException(
            status_code=failure_status, detail="Game not found")
    return game


def find_player(player_id: int, failure_status=status.HTTP_400_BAD_REQUEST) -> Player:
    """
    Find a player by ID

    Args:
    game_id (int): The ID of the game the player is in
    player_id (PlayerID): The ID of the player to find

    Returns:
    Player: The player with the given ID
    """

    player = select(p for p in Player if p.id == player_id).get()
    if player is None:
        raise HTTPException(
            status_code=failure_status, detail="Player not found")
    return player


def find_card(card_id: int, failure_status=status.HTTP_400_BAD_REQUEST) -> Player:
    """
    Find a player by ID

    Args:
    game_id (int): The ID of the game the player is in
    player_id (PlayerID): The ID of the player to find

    Returns:
    Player: The player with the given ID
    """

    card = select(c for c in Card if c.id == card_id).get()
    if card is None:
        raise HTTPException(
            status_code=failure_status, detail="Card not found")
    return card
