from fastapi import HTTPException
from pony.orm import select 
from models import Game, Player
from schemas.schemas import PlayerID
from fastapi import HTTPException, status
import random

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
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Game not found")
    return game


def find_player(player_id: PlayerID) -> Player:
    """
    Find a player by ID

    Args:
    game_id (int): The ID of the game the player is in
    player_id (PlayerID): The ID of the player to find

    Returns:
    Player: The player with the given ID
    """

    player = select(p for p in Player if p.id == player_id.playerID).get()
    if player is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Player not found")
    return player


def draw_card(game_id: int, player_id: PlayerID) -> None:
    """
    Draw a card from the game deck and assign it to a player

    Args:
    game_id (int): The ID of the game to draw a card from
    player_id (PlayerID): The ID of the player to assign the card to
    """
    
    game = find_game(game_id)
    player = find_player(player_id)
    
    card = random.choice(list(game.cards))

    card.player = player
    game.cards.remove(card)
    player.cards.add(card)


def handle_errors(game_id: int, player_id: PlayerID) -> None:
    """
    Check if the pre-conditions for drawing a card are met

    Args:
    game_id (int): The ID of the game to draw a card from
    player_id (PlayerID): The ID of the player to assign the card to
    """

    game = find_game(game_id)
    player = find_player(player_id)

    if player not in game.players:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Player not in game")
    
    if player.cards.count() > 4:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Player already has a card")

    if not game.cards:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No cards left in deck")