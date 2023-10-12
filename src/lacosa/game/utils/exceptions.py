from fastapi import HTTPException, status
from models import Game, Player


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


def validate_player_in_game(game: Game, player: Player):
    if player not in game.players:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Player not in game")


def validate_ammount_of_cards(player: Player):
    # FIXME: player can have 5 cards
    if player.cards.count() > 4:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Player already has a card")


def validate_deck_not_empty(game: Game):
    if not game.cards:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="No cards left in deck")
