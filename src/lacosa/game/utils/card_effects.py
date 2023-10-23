from models import Player, Game
from collections.abc import Callable
from typing import Dict

CardEffectFunc = Callable[[Player, Game], None]


def update_player_positions_after_death(player, game):
    for p in game.players:
        if p.position > player.position:
            p.position -= 1
    player.position = 0


def add_player_hand_to_deck(player: Player, game: Game) -> None:
    for card in player.cards:
        game.cards.add(card)
    player.cards.clear()


def switch_player_positions(player1: Player, player2: Player) -> None:
    player1.position, player2.position = player2.position, player1.position


def apply_lanzallamas_effect(current_player: Player, target_player: Player, game: Game) -> None:
    target_player.is_alive = False
    add_player_hand_to_deck(target_player, game)
    update_player_positions_after_death(target_player, game)


def apply_switch_position_cards_effect(current_player: Player, target_player: Player, game: Game) -> None:
    switch_player_positions(current_player, target_player)


def do_nothing(target_player: Player, game: Game):
    pass


def get_card_effect_function(card_name: str) -> CardEffectFunc:
    _card_effects: Dict[str, CardEffectFunc] = {
        "Lanzallamas": apply_lanzallamas_effect,
        "Cambio de lugar": apply_switch_position_cards_effect,
        "Más vale que corras": apply_switch_position_cards_effect,
    }

    return _card_effects.get(card_name, do_nothing)


def execute_card_effect(card, player ,target_player, game) -> None:
        """
        Plays a card on the game
        Args:
        play_request (PlayCardRequest): Input data to validate
        game_id (int): The id of the game to validate
        """
        effect_func: CardEffectFunc = get_card_effect_function(card.name)
        effect_func(player, target_player, game)

        player.cards.remove(card)
        game.cards.add(card)
        game.last_played_card = card