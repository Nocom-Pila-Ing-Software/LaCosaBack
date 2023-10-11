from models import Game, Player
from schemas.schemas import PlayerID
from fastapi import HTTPException, status
import random
import lacosa.game.utils.utils as utils


def draw_card(game_id: int, player_id: PlayerID) -> None:
    """
    Draw a card from the game deck and assign it to a player

    Args:
    game_id (int): The ID of the game to draw a card from
    player_id (PlayerID): The ID of the player to assign the card to
    """

    game = utils.find_game(game_id)
    player = utils.find_player(player_id)

    _handle_errors(game, player)

    card = random.choice(list(game.cards))

    card.player = player
    game.cards.remove(card)
    player.cards.add(card)


def _handle_errors(game: Game, player: Player) -> None:
    """
    Check if the pre-conditions for drawing a card are met

    Args:
    game_id (int): The ID of the game to draw a card from
    player_id (PlayerID): The ID of the player to assign the card to
    """
    if player not in game.players:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Player not in game")

    if player.cards.count() > 4:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Player already has a card")

    if not game.cards:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="No cards left in deck")
