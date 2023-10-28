from ..deck import Deck
from lacosa.game.schemas import GenericCardRequest
import lacosa.utils as utils
import lacosa.game.utils.exceptions as exceptions
from models import Game, Player, Card, Event


def discard_card_util(discard_request: GenericCardRequest, room_id: int):
    game = utils.find_game(room_id)
    player = utils.find_player(discard_request.playerID)
    card = utils.find_card(discard_request.cardID)

    _handle_errors(game, player, card)

    Deck.discard_card(card, player, game)

    game.current_action = "trade"

    next_player = game.players.select(
        lambda p: p.position == player.position + 1).first()
    if next_player is None:
        next_player = game.players.select(
            lambda p: p.position == 1).first()
        
    game.events.create(type="trade", player1=player, player2=next_player)


def _handle_errors(game: Game, player: Player, card: Card):
    exceptions.validate_player_in_game(game, player)
    exceptions.validate_card_in_hand(card, player)
    exceptions.validate_player_is_in_turn(player, game)
