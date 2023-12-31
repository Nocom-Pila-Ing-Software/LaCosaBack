from ..deck import Deck
from lacosa.game.schemas import GenericCardRequest
import lacosa.utils as utils
import lacosa.game.utils.exceptions as exceptions
from models import Game, Player, Card
from lacosa.game.utils import turn_handler
from lacosa.game.utils import obstacles


def set_turn_state(game, next_player, player):
    if not obstacles.is_blocked_by_obstacle(game, player.position, next_player.position):
        game.current_action = "trade"
        game.events.create(type="trade", player1=player, player2=next_player)
    else:
        game.current_action = "draw"
        game.current_player = next_player.id


def discard_card_util(discard_request: GenericCardRequest, room_id: int):
    game = utils.find_game(room_id)
    player = utils.find_player(discard_request.playerID)
    card = utils.find_card(discard_request.cardID)

    _handle_errors(game, player, card)

    Deck.discard_card(card, player, game)

    next_player = turn_handler.get_next_player(game, player.position)

    set_turn_state(game, next_player, player)


def _handle_errors(game: Game, player: Player, card: Card):
    exceptions.validate_player_in_game(game, player)
    exceptions.validate_card_in_hand(card, player)
    exceptions.validate_player_is_in_turn(player, game)
