from pony.orm import select
from models import Game, Player, Card
from fastapi import HTTPException, status


def find_game(game_id: int) -> Game:
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
            status_code=status.HTTP_404_NOT_FOUND, detail="Game not found")
    return game


def find_player(player_id: int) -> Player:
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
            status_code=status.HTTP_400_BAD_REQUEST, detail="Player not found")
    return player


def find_card(card_id: int) -> Player:
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
            status_code=status.HTTP_400_BAD_REQUEST, detail="Card not found")
    return card
