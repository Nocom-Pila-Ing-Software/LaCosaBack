from lacosa.game.utils.deck import Deck
from lacosa import utils
from lacosa.schemas import PlayerID
from lacosa.game.utils.card import effects


def draw_card_util(player_id: PlayerID, room_id: int):
    game = utils.find_game(room_id)
    player = utils.find_player(player_id.playerID)
    card = Deck.get_card_from_deck(game, player)
    if card.type == "panic":
        effects.execute_card_effect(card, player, None, game)
    else:
        game.cards.remove(card)
        player.cards.add(card)
        game.current_action = "action"
