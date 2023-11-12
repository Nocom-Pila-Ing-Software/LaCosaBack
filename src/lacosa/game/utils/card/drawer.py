from lacosa.game.utils.deck import Deck
from lacosa import utils
from lacosa.schemas import PlayerID


def draw_card_util(player_id: PlayerID, room_id: int):
    Deck.draw_card(room_id, player_id.playerID)
    game = utils.find_game(room_id)
    game.current_action = "action"
