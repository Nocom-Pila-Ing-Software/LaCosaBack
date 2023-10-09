from fastapi import HTTPException
from models import Game, Player, Card
from schemas.game import PlayCardRequest
from .card_effects import apply_lanzallamas_effect
from pony.orm import db_session


def play_card(play_request: PlayCardRequest, game_id: int) -> None:
    """
    Plays a card on the game

    Args:
    play_request (PlayCardRequest): Input data to validate
    game_id (int): The id of the game to validate
    """
    game = Game.get(id=game_id)

    if Card.get(id=play_request.cardID).name == "Lanzallamas":
        apply_lanzallamas_effect(play_request.targetPlayerID)
        modify_player_position(Player.get(id=play_request.playerID), game)

    player = Player.get(id=play_request.playerID)
    card = Card.get(id=play_request.cardID)

    player.cards.remove(card)
    game.cards.add(card)
    game.last_played_card = card

    game.current_player = get_next_player(game, player)

def modify_player_position(player, game):
    for p in game.players:
        if p.position > player.position:
            p.position -= 1    

def get_next_player(game, player):
    next_player = game.players.select(lambda p: p.position == player.position + 1).first()
    if next_player is None:
        next_player = game.players.select(lambda p: p.position == 1).first()
    return next_player.id

def get_game(game_id: int):
    game = Game.get(id=game_id)
    if not game:
        raise HTTPException(
            status_code=404,
            detail="Game not found"
        )
    return game


def get_player(player_id: int):
    player = Player.get(id=player_id)
    if not player:
        raise HTTPException(
            status_code=400,
            detail="Player not found"
        )
    return player


def validate_player_in_game(player, game):
    if player.game != game:
        raise HTTPException(
            status_code=400,
            detail="Player is not in this game"
        )


def validate_player_has_card(player, card_id):
    if not player.cards.filter(id=card_id).exists():
        raise HTTPException(
            status_code=400,
            detail="Player does not have that card"
        )


def validate_player_alive(player):
    if not player.is_alive:
        raise HTTPException(
            status_code=400,
            detail="Player is dead"
        )


def handle_errors(play_request: PlayCardRequest, game_id: int) -> None:
    """
    Checks for errors in play_request and raises HTTPException if needed

    Args:
    play_request (PlayCardRequest): Input data to validate
    game_id (int): The id of the game to validate

    Raises:
    HTTPException(status_code=400): If the player is not found or not is allowed to play
    HTTPException(status_code=404): If the game is not found
    """

    game = get_game(game_id)
    player = get_player(play_request.playerID)
    target_player = get_player(play_request.targetPlayerID)

    validate_player_in_game(player, game)
    validate_player_in_game(target_player, game)
    validate_player_has_card(player, play_request.cardID)
    validate_player_alive(target_player)
