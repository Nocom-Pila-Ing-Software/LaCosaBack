from models import Player, Game
from collections.abc import Callable
from typing import Dict
from pony.orm import select, commit
from lacosa.game.utils.card_shower import show_cards_to_players
from lacosa.game.utils import event_creator, turn_handler


CardEffectFunc = Callable[[Player, Game], None]


def update_player_positions_after_death(player, game):
    for p in game.players:
        if p.position > player.position:
            p.position -= 1
    player.position = 0

    commit()


def add_player_hand_to_deck(player: Player, game: Game) -> None:
    for card in player.cards:
        game.cards.add(card)
    player.cards.clear()


def switch_player_positions(player1: Player, player2: Player) -> None:
    player1.position, player2.position = player2.position, player1.position


def apply_lanzallamas_effect(
    current_player: Player, target_player: Player, game: Game
) -> None:
    target_player.is_alive = False
    add_player_hand_to_deck(target_player, game)
    update_player_positions_after_death(target_player, game)


def apply_switch_position_cards_effect(
    current_player: Player, target_player: Player, game: Game
) -> None:
    switch_player_positions(current_player, target_player)


def apply_anticipate_trade_effect(
    current_player: Player, target_player: Player, game: Game
) -> None:
    event = select(event for event in game.events if event.is_completed is False).get()
    event.is_completed = True
    event.is_successful = True
    game.events.create(
        player1=current_player,
        player2=target_player,
        card1=None,
        card2=None,
        is_completed=False,
        is_successful=False,
        type="trade",
    )


def apply_vigila_tus_espaldas_effect(
    current_player: Player, target_player: Player, game: Game
) -> None:
    game.game_order = "left" if game.game_order == "right" else "right"


def apply_whisky_effect(
    current_player: Player, target_player: Player, game: Game
) -> None:
    players_to_show = [
        player
        for player in game.players
        if player != current_player and player.is_alive
    ]
    cards_to_show = [card for card in current_player.cards]
    show_cards_to_players(cards_to_show, players_to_show)


def apply_sospecha_effect(
    current_player: Player, target_player: Player, game: Game
) -> None:
    card_to_show = target_player.cards.random(1)
    show_cards_to_players(card_to_show, [current_player])


def apply_analysis_effect(
    current_player: Player, target_player: Player, game: Game
) -> None:
    cards_to_show = [card for card in target_player.cards]
    show_cards_to_players(cards_to_show, [current_player])


def apply_aterrador_effect(
    current_player: Player, target_player: Player, game: Game
) -> None:
    event = select(event for event in game.events if event.is_completed is False).get()
    event.is_completed = True
    event.is_successful = False
    card_to_show = [event.card1]
    player_to_show = [event.player2]
    show_cards_to_players(card_to_show, player_to_show)


def apply_fallaste_effect(
    current_player: Player, target_player: Player, game: Game
) -> None:
    """
    ¡Fallaste!: Sólo puedes jugar esta carta como respuesta a un ofrecimiento de
    intercambio de cartas. Niégate a un intercambio de cartas solicitado por un jugador o
    por el efecto de una carta. El siguiente jugador después de ti (siguiendo el orden de
    juego) debe intercambiar cartas en lugar de hacerlo tú. Si este jugador recibe una
    carta “¡Infectado!” durante el intercambio, no queda Infectado, ¡pero sabrá que ha
    recibido una carta de La Cosa o de un jugador Infectado! Si hay “obstáculos” en el
    camino, como una “Puerta atrancada” o “Cuarentena”, no se produce ningún
    intercambio, y el siguiente turno lo jugará el jugador siguiente a aquel que inició el
    intercambio.
    """
    event = select(event for event in game.events if event.is_completed is False).get()
    event.is_completed = True
    event.is_successful = False
    next_target_player = turn_handler.get_next_player(game, target_player.position)
    game.events.create(
        player1=current_player.id,
        player2=next_target_player.id,
        card1=event.card1,
        card2=None,
        is_completed=False,
        is_successful=False,
        type="trade",
    )
    game.current_action = "defense"
    game.current_player = next_target_player.id


def do_nothing(*args, **kwargs) -> None:
    pass


def get_card_effect_function(card_name: str) -> CardEffectFunc:
    _card_effects: Dict[str, CardEffectFunc] = {
        "Lanzallamas": apply_lanzallamas_effect,
        "Cambio de lugar": apply_switch_position_cards_effect,
        "Mas vale que corras": apply_switch_position_cards_effect,
        "Vigila tus espaldas": apply_vigila_tus_espaldas_effect,
        "Aqui estoy bien": do_nothing,
        "Nada de barbacoas": do_nothing,
        "No gracias": do_nothing,
        "Seduccion": apply_anticipate_trade_effect,
        "Whisky": apply_whisky_effect,
        "Sospecha": apply_sospecha_effect,
        "Analisis": apply_analysis_effect,
        "Aterrador": apply_aterrador_effect,
        "Fallaste": apply_fallaste_effect,
    }

    return _card_effects.get(card_name, do_nothing)


def execute_card_effect(card, player, target_player, game) -> None:
    """
    Plays a card on the game
    Args:
    play_request (PlayCardRequest): Input data to validate
    game_id (int): The id of the game to validate
    """
    effect_func: CardEffectFunc = get_card_effect_function(card.name)
    if effect_func is not None:
        effect_func(player, target_player, game)

    player.cards.remove(card)
    game.cards.add(card)
    game.last_played_card = card
