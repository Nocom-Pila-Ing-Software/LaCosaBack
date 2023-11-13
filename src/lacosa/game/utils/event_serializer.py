from models import Event
from collections.abc import Callable
from lacosa.game.schemas import EventTypes
from typing import Dict


def do_nothing(event):
    return ""


def get_defense_text(event, result):
    result.extend(
        ["pero", event.player2.username, "se defendio con", event.card2.name]
    )


def serialize_action(event):
    result = [
        event.player1.username,
        "jugó",
        f"'{event.card1.name}'",
    ]
    if event.player1 != event.player2:
        result.extend([
            "sobre",
            event.player2.username,
        ])
    if not event.is_successful:
        get_defense_text(event, result)

    return " ".join(result)


def serialize_trade(event):
    result = [
        event.player1.username,
        "realizó",
        "un intercambio con",
        event.player2.username,
    ]
    if not event.is_successful:
        REALIZO_POSITION = 1
        result[REALIZO_POSITION] = "inicio"
        get_defense_text(event, result)

    return " ".join(result)


def serialize_revelations_start(event):
    return "Una ronda de revelaciones ha comenzado.."


def serialize_revelations_end(event):
    return f"La ronda de revelaciones ha finalizado gracias a {event.player1}"


def serialize_play_panic(event):
    return f"{event.player1.username} ha sacado la carta de panico '{event.card1}'"


def serialize_draw_card(event):
    return f"{event.player1.username} saca una carta del mazo"


def serialize_door(event):
    return f"Se ha puesto una puerta atrancada entre {event.player1.username} y {event.player2.username}"


def serialize_switch_order(event):
    return f"{event.player1.username} cambió el orden del juego"


def serialize_death(event):
    return f"{event.player1.username} ha muerto"


def serialize_show_hand(event):
    extra = ""
    if event.player2:
        extra = f"a {event.player1.username}"
    return f"{event.player2.username} muestra su mano a {extra}"


def serialize_show_card(event):
    extra = ""
    if event.player2:
        extra = f"a {event.player1.username}"
    return f"{event.player2.username} muestra una carta {extra}"


def serialize_switch_place(event):
    return f"{event.player1.username} cambia de lugar con {event.player2.username}"


_FUNCS: Dict[str, Callable[[Event], str]] = {
    EventTypes.action: serialize_action,
    EventTypes.trade: serialize_trade,
    EventTypes.revelations_start: serialize_revelations_start,
    EventTypes.revelations_end: serialize_revelations_end,
    EventTypes.play_panic: serialize_play_panic,
    EventTypes.draw_card: serialize_draw_card,
    EventTypes.door: serialize_door,
    EventTypes.switch_order: serialize_switch_order,
    EventTypes.death: serialize_death,
    EventTypes.show_hand: serialize_show_hand,
    EventTypes.show_card: serialize_show_card,
    EventTypes.switch_place: serialize_switch_place,
}


def get_serialization_func(type_: str) -> Callable[[Event], str]:
    return _FUNCS.get(type_)


def get_event_text(event):
    func = get_serialization_func(event.type)
    result = func(event)

    return result
