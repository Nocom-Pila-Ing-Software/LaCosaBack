import json
from pathlib import Path
from fastapi import HTTPException, status
from models import Game, Player, Card


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


def validate_player_in_game(game: Game, player: Player, default_status_code=status.HTTP_404_NOT_FOUND):
    if game is None:
        # Verify that the player is in a game
        if player.game is None:
            raise HTTPException(status_code=default_status_code,
                                detail="Player not in game")
    elif player not in game.players:
        raise HTTPException(status_code=default_status_code,
                            detail="Player not in game")


def validate_card_in_hand(card: Card, player: Player):
    if card not in player.cards:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Card not in hand")


def validate_player_is_in_turn(player: Player, game: Game):
    if game.current_player != player.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Can't discard card, it's not your turn"
        )


def validate_ammount_of_cards(player: Player):
    if player.cards.count() > 4:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Player already has a card")


def validate_deck_not_empty(game: Game):
    if not game.cards:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="No cards left in deck")


def validate_current_action(game: Game, action: str, action2: str = None):
    if game.current_action != action and game.current_action != action2:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Player not has permission to execute this action")


def validate_current_player(game: Game, player: Player):
    if game.current_player != player.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Player not has permission to execute this action")


def validate_correct_defense_card(card, event):
    config_path = Path(__file__).resolve().parent.parent / \
        'utils' / 'config_deck.json'

    with open(config_path) as config_file:
        config = json.load(config_file)

    if (event.type == "action" and card.name not in config["cards"][event.card1.name]["defensible_by"]) or (event.type == "trade" and card.name != "No, gracias"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Player not has permission to execute this action")


def validate_correct_type(card, type):
    if card.type != type:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Player not has permission to execute this action")
    
def validate_card_allowed_to_trade(card, event, player):
    if card.name == "la cosa":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Player not has permission to execute this action")
    
    if card.name == "infectado" and player.role == "human":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Player not has permission to execute this action")
    
    amount_infectado_cards_in_hand = 0
    for card in player.cards:
        if card.name == "infectado":
            amount_infectado_cards_in_hand += 1

    if card.name == "infectado" and player.role == "the thing":
        if event.player1.role != "human" and event.player2.role != "human":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Player not has permission to execute this action")
    if card.name == "infectado" and amount_infectado_cards_in_hand == 1 and player.role == "infected":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Player not has permission to execute this action")
    if card.name == "infectado" and (event.player1.role != "the thing" and event.player2.role != "the thing") and player.role == "infected":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Player not has permission to execute this action")
    if card.name == "infectado" and player.role == "human":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Player not has permission to execute this action")

