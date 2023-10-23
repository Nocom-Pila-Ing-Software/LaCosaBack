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


def validate_player_in_game(game: Game, player: Player):
    if player not in game.players:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Player not in game")


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
    
def validate_current_action(game: Game, action: str,action2: str = None):
    if game.current_action != action and game.current_action != action2:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Player not has permission to execute this action")
    
def validate_current_player(game: Game, player: Player):
    if game.current_player != player.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Player not has permission to execute this action")
    

def validate_correct_defense_card(card, event):
    if event.type == "trade" and card.name == "No, gracias":
        return
    if event.type == "action" and card.name == "No, gracias":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Player not has permission to execute this action")
