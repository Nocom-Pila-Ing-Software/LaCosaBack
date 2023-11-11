from time import sleep
from main import app
from fastapi.testclient import TestClient
from models import Game, Card
from pony.orm import db_session, select, commit, delete
import pytest
from .game_fixtures import (
    db_game_creation_with_trade_event,
    db_game_creation_with_trade_event_2,
    db_game_creation_with_trade_event_3,
    get_defend_trade_card_game_creation,
)

client = TestClient(app)


def next_player(game, game_event):
    next_player = game.players.select(
        lambda p: p.position == game_event.player1.position + 1
    ).first()
    if next_player is None:
        next_player = game.players.select(lambda p: p.position == 1).first()
    return next_player.id


def get_game_and_cards():
    game = Game.get(id=1)
    game_event = select(e for e in game.events).first()
    cards_player_1 = list(
        select(e for e in game_event.player1.cards).sort_by(lambda x: x.id)
    )
    cards_player_2 = list(
        select(e for e in game_event.player2.cards).sort_by(lambda x: x.id)
    )
    return game, game_event, cards_player_1, cards_player_2


def select_card(card_id):
    return select(c for c in Card if c.id == card_id).first()


def assert_game_state(
    game,
    game_event,
    is_completed,
    player1,
    player2,
    card1,
    card2,
    action,
    current_player,
    is_successful=False,
):
    assert game_event.is_completed == is_completed
    assert game_event.is_successful == is_successful

    assert game_event.card1 == card1
    assert game_event.card2 == card2

    assert game.current_action == action
    assert game.current_player == current_player


def assert_game_cards(game, game_event, card_player_1, card_player_2):
    assert len(game_event.player1.cards) == 4
    assert len(game_event.player2.cards) == 4

    assert card_player_1 in game_event.player1.cards
    assert card_player_2 in game_event.player2.cards

    assert card_player_1 not in game_event.player2.cards
    assert card_player_2 not in game_event.player1.cards


def test_successfull_trade(db_game_creation_with_trade_event):
    player1_id = None
    player2_id = None
    card_player_1_id = None
    card_player_2_id = None
    with db_session:
        game, game_event, cards_player_1, cards_player_2 = get_game_and_cards()

        player1_id = game_event.player1.id
        player2_id = game_event.player2.id

        card_player_1_id = cards_player_1[1].id
        card_player_2_id = cards_player_2[3].id

    response1 = client.put(
        "/game/1/trade-card", json={"playerID": player1_id, "cardID": card_player_1_id}
    )

    assert response1.status_code == 200

    with db_session:
        game, game_event, cards_player_1, cards_player_2 = get_game_and_cards()

        assert_game_state(
            game,
            game_event,
            is_completed=False,
            player1=game_event.player1,
            player2=game_event.player2,
            card1=select_card(card_player_1_id),
            card2=None,
            action="defense",
            current_player=game_event.player2.id,
        )

        assert_game_cards(
            game,
            game_event,
            select_card(card_player_1_id),
            select_card(card_player_2_id),
        )

    response2 = client.put(
        "/game/1/defend-card", json={"playerID": player2_id, "cardID": -1}
    )

    assert response2.status_code == 200

    with db_session:
        game, game_event, cards_player_1, cards_player_2 = get_game_and_cards()

        assert_game_state(
            game,
            game_event,
            is_completed=False,
            player1=game_event.player1,
            player2=game_event.player2,
            card1=select_card(card_player_1_id),
            card2=None,
            action="trade",
            current_player=game_event.player2.id,
        )

        assert_game_cards(
            game,
            game_event,
            select_card(card_player_1_id),
            select_card(card_player_2_id),
        )

    response3 = client.put(
        "/game/1/trade-card", json={"playerID": player2_id, "cardID": card_player_2_id}
    )

    assert response3.status_code == 200

    with db_session:
        game, game_event, cards_player_1, cards_player_2 = get_game_and_cards()
        next_position = next_player(game, game_event)

        assert_game_state(
            game,
            game_event,
            is_completed=True,
            player1=game_event.player1,
            player2=game_event.player2,
            card1=select_card(card_player_1_id),
            card2=select_card(card_player_2_id),
            action="draw",
            current_player=next_position,
            is_successful=True,
        )

        assert_game_cards(
            game,
            game_event,
            select_card(card_player_2_id),
            select_card(card_player_1_id),
        )


def test_unsuccessfull_trade_No_gracias(db_game_creation_with_trade_event):
    player1_id = None
    player2_id = None
    card_player_1_id = None
    card_player_2_id = None
    with db_session:
        game, game_event, cards_player_1, cards_player_2 = get_game_and_cards()

        player1_id = game_event.player1.id
        player2_id = game_event.player2.id

        card_player_1_id = cards_player_1[1].id
        card_player_2_id = cards_player_2[3].id

    response1 = client.put(
        "/game/1/trade-card", json={"playerID": player1_id, "cardID": card_player_1_id}
    )

    assert response1.status_code == 200

    with db_session:
        game, game_event, cards_player_1, cards_player_2 = get_game_and_cards()

        assert_game_state(
            game,
            game_event,
            is_completed=False,
            player1=game_event.player1,
            player2=game_event.player2,
            card1=select_card(card_player_1_id),
            card2=None,
            action="defense",
            current_player=game_event.player2.id,
        )

        assert_game_cards(
            game,
            game_event,
            select_card(card_player_1_id),
            select_card(card_player_2_id),
        )

    response2 = client.put(
        "/game/1/defend-card", json={"playerID": player2_id, "cardID": card_player_2_id}
    )

    assert response2.status_code == 200

    with db_session:
        game, game_event, cards_player_1, cards_player_2 = get_game_and_cards()

        next_position = next_player(game, game_event)

        assert_game_state(
            game,
            game_event,
            is_completed=True,
            player1=game_event.player1,
            player2=game_event.player2,
            card1=select_card(card_player_1_id),
            card2=select_card(card_player_2_id),
            action="draw",
            current_player=next_position,
            is_successful=False,
        )

        assert select_card(card_player_1_id) in cards_player_1
        assert select_card(card_player_1_id) not in cards_player_2
        assert select_card(card_player_2_id) not in cards_player_2
        assert len(cards_player_1) == 4
        assert len(cards_player_2) == 4


def test_unsuccessfull_trade_Aterrador(db_game_creation_with_trade_event):
    player1_id = None
    player2_id = None
    card_player_1_id = None
    card_player_2_id = None
    with db_session:
        game, game_event, cards_player_1, cards_player_2 = get_game_and_cards()

        player1_id = game_event.player1.id
        player2_id = game_event.player2.id

        card_player_1_id = cards_player_1[1].id
        card_player_2_id = cards_player_2[2].id

    response1 = client.put(
        "/game/1/trade-card", json={"playerID": player1_id, "cardID": card_player_1_id}
    )

    assert response1.status_code == 200

    with db_session:
        game, game_event, cards_player_1, cards_player_2 = get_game_and_cards()

        assert_game_state(
            game,
            game_event,
            is_completed=False,
            player1=game_event.player1,
            player2=game_event.player2,
            card1=select_card(card_player_1_id),
            card2=None,
            action="defense",
            current_player=game_event.player2.id,
        )

        assert_game_cards(
            game,
            game_event,
            select_card(card_player_1_id),
            select_card(card_player_2_id),
        )

    response2 = client.put(
        "/game/1/defend-card", json={"playerID": player2_id, "cardID": card_player_2_id}
    )

    assert response2.status_code == 200

    with db_session:
        game, game_event, cards_player_1, cards_player_2 = get_game_and_cards()

        next_position = next_player(game, game_event)

        assert_game_state(
            game,
            game_event,
            is_completed=True,
            player1=game_event.player1,
            player2=game_event.player2,
            card1=select_card(card_player_1_id),
            card2=select_card(card_player_2_id),
            action="draw",
            current_player=next_position,
            is_successful=False,
        )

        player2 = game_event.player2
        for card in player2.shown_cards:
            assert card.id == card_player_1_id

        assert select_card(card_player_1_id) in cards_player_1
        assert select_card(card_player_1_id) not in cards_player_2
        assert select_card(card_player_2_id) not in cards_player_2
        assert len(cards_player_1) == 4
        assert len(cards_player_2) == 4


def test_trade_with_invalid_room_id(db_game_creation_with_trade_event):
    player1_id = None
    player2_id = None
    card_player_1_id = None
    card_player_2_id = None
    with db_session:
        game, game_event, cards_player_1, cards_player_2 = get_game_and_cards()

        player1_id = game_event.player1.id
        player2_id = game_event.player2.id

        card_player_1_id = cards_player_1[1].id
        card_player_2_id = cards_player_2[3].id

    response1 = client.put(
        "/game/2/trade-card", json={"playerID": player1_id, "cardID": card_player_1_id}
    )

    assert response1.status_code == 404
    assert response1.json() == {"detail": "Game not found"}

    with db_session:
        game, game_event, cards_player_1, cards_player_2 = get_game_and_cards()
        assert_game_state(
            game,
            game_event,
            is_completed=False,
            player1=game_event.player1,
            player2=game_event.player2,
            card1=None,
            card2=None,
            action="trade",
            current_player=game_event.player1.id,
        )

        assert_game_cards(
            game,
            game_event,
            select_card(card_player_1_id),
            select_card(card_player_2_id),
        )

    response1 = client.put(
        "/game/1/trade-card", json={"playerID": player1_id, "cardID": card_player_1_id}
    )

    assert response1.status_code == 200

    with db_session:
        game, game_event, cards_player_1, cards_player_2 = get_game_and_cards()

        assert_game_state(
            game,
            game_event,
            is_completed=False,
            player1=game_event.player1,
            player2=game_event.player2,
            card1=select_card(card_player_1_id),
            card2=None,
            action="defense",
            current_player=game_event.player2.id,
        )

        assert_game_cards(
            game,
            game_event,
            select_card(card_player_1_id),
            select_card(card_player_2_id),
        )

    response2 = client.put(
        "/game/1/defend-card", json={"playerID": player2_id, "cardID": -1}
    )

    assert response2.status_code == 200

    with db_session:
        game, game_event, cards_player_1, cards_player_2 = get_game_and_cards()

        assert_game_state(
            game,
            game_event,
            is_completed=False,
            player1=game_event.player1,
            player2=game_event.player2,
            card1=select_card(card_player_1_id),
            card2=None,
            action="trade",
            current_player=game_event.player2.id,
        )

        assert_game_cards(
            game,
            game_event,
            select_card(card_player_1_id),
            select_card(card_player_2_id),
        )

    response3 = client.put(
        "/game/2/trade-card", json={"playerID": player2_id, "cardID": card_player_2_id}
    )

    assert response3.status_code == 404
    assert response3.json() == {"detail": "Game not found"}

    with db_session:
        game, game_event, cards_player_1, cards_player_2 = get_game_and_cards()

        assert_game_state(
            game,
            game_event,
            is_completed=False,
            player1=game_event.player1,
            player2=game_event.player2,
            card1=select_card(card_player_1_id),
            card2=None,
            action="trade",
            current_player=game_event.player2.id,
        )

        assert_game_cards(
            game,
            game_event,
            select_card(card_player_1_id),
            select_card(card_player_2_id),
        )


def test_trade_with_invalid_player_id(db_game_creation_with_trade_event):
    player1_id = None
    card_player_1_id = None
    card_player_2_id = None
    with db_session:
        game, game_event, cards_player_1, cards_player_2 = get_game_and_cards()

        player1_id = game_event.player1.id

        card_player_1_id = cards_player_1[1].id
        card_player_2_id = cards_player_2[3].id

    response1 = client.put(
        "/game/1/trade-card", json={"playerID": 30000, "cardID": card_player_1_id}
    )

    assert response1.status_code == 400
    assert response1.json() == {"detail": "Player not found"}

    with db_session:
        game, game_event, cards_player_1, cards_player_2 = get_game_and_cards()

        assert_game_state(
            game,
            game_event,
            is_completed=False,
            player1=game_event.player1,
            player2=game_event.player2,
            card1=None,
            card2=None,
            action="trade",
            current_player=game_event.player1.id,
        )

        assert_game_cards(
            game,
            game_event,
            select_card(card_player_1_id),
            select_card(card_player_2_id),
        )

    response1 = client.put(
        "/game/1/trade-card", json={"playerID": player1_id, "cardID": card_player_1_id}
    )

    assert response1.status_code == 200

    with db_session:
        game, game_event, cards_player_1, cards_player_2 = get_game_and_cards()

        assert_game_state(
            game,
            game_event,
            is_completed=False,
            player1=game_event.player1,
            player2=game_event.player2,
            card1=select_card(card_player_1_id),
            card2=None,
            action="defense",
            current_player=game_event.player2.id,
        )

        assert_game_cards(
            game,
            game_event,
            select_card(card_player_1_id),
            select_card(card_player_2_id),
        )

    response2 = client.put(
        "/game/1/defend-card", json={"playerID": game_event.player2.id, "cardID": -1}
    )

    assert response2.status_code == 200

    with db_session:
        game, game_event, cards_player_1, cards_player_2 = get_game_and_cards()

        assert_game_state(
            game,
            game_event,
            is_completed=False,
            player1=game_event.player1,
            player2=game_event.player2,
            card1=select_card(card_player_1_id),
            card2=None,
            action="trade",
            current_player=game_event.player2.id,
        )

        assert_game_cards(
            game,
            game_event,
            select_card(card_player_1_id),
            select_card(card_player_2_id),
        )

    response3 = client.put(
        "/game/1/trade-card", json={"playerID": 8998, "cardID": card_player_2_id}
    )

    assert response3.status_code == 400
    assert response3.json() == {"detail": "Player not found"}

    with db_session:
        game, game_event, cards_player_1, cards_player_2 = get_game_and_cards()
        assert_game_state(
            game,
            game_event,
            is_completed=False,
            player1=game_event.player1,
            player2=game_event.player2,
            card1=select_card(card_player_1_id),
            card2=None,
            action="trade",
            current_player=game_event.player2.id,
        )

        assert_game_cards(
            game,
            game_event,
            select_card(card_player_1_id),
            select_card(card_player_2_id),
        )


def test_trade_with_card_not_in_hand(db_game_creation_with_trade_event):
    player1_id = None
    player2_id = None
    card_player_1_id = None
    card_player_2_id = None
    with db_session:
        game, game_event, cards_player_1, cards_player_2 = get_game_and_cards()

        player1_id = game_event.player1.id
        player2_id = game_event.player2.id

        card_player_1_id = cards_player_1[1].id
        card_player_2_id = cards_player_2[3].id

    response1 = client.put(
        "/game/1/trade-card", json={"playerID": player1_id, "cardID": card_player_2_id}
    )

    assert response1.status_code == 400
    assert response1.json() == {"detail": "Player does not have that card"}

    with db_session:
        game, game_event, cards_player_1, cards_player_2 = get_game_and_cards()

        assert_game_state(
            game,
            game_event,
            is_completed=False,
            player1=game_event.player1,
            player2=game_event.player2,
            card1=None,
            card2=None,
            action="trade",
            current_player=game_event.player1.id,
        )

        assert_game_cards(
            game,
            game_event,
            select_card(card_player_1_id),
            select_card(card_player_2_id),
        )

    response1 = client.put(
        "/game/1/trade-card", json={"playerID": player1_id, "cardID": card_player_1_id}
    )

    assert response1.status_code == 200

    with db_session:
        game, game_event, cards_player_1, cards_player_2 = get_game_and_cards()

        assert_game_state(
            game,
            game_event,
            is_completed=False,
            player1=game_event.player1,
            player2=game_event.player2,
            card1=select_card(card_player_1_id),
            card2=None,
            action="defense",
            current_player=game_event.player2.id,
        )

        assert_game_cards(
            game,
            game_event,
            select_card(card_player_1_id),
            select_card(card_player_2_id),
        )

    response2 = client.put(
        "/game/1/defend-card", json={"playerID": player2_id, "cardID": -1}
    )

    assert response2.status_code == 200

    with db_session:
        game, game_event, cards_player_1, cards_player_2 = get_game_and_cards()

        assert_game_state(
            game,
            game_event,
            is_completed=False,
            player1=game_event.player1,
            player2=game_event.player2,
            card1=select_card(card_player_1_id),
            card2=None,
            action="trade",
            current_player=game_event.player2.id,
        )

        assert_game_cards(
            game,
            game_event,
            select_card(card_player_1_id),
            select_card(card_player_2_id),
        )

    response3 = client.put(
        "/game/1/trade-card", json={"playerID": player2_id, "cardID": card_player_1_id}
    )

    assert response3.status_code == 400
    assert response3.json() == {"detail": "Player does not have that card"}

    with db_session:
        game, game_event, cards_player_1, cards_player_2 = get_game_and_cards()

        assert_game_state(
            game,
            game_event,
            is_completed=False,
            player1=game_event.player1,
            player2=game_event.player2,
            card1=select_card(card_player_1_id),
            card2=None,
            action="trade",
            current_player=game_event.player2.id,
        )

        assert_game_cards(
            game,
            game_event,
            select_card(card_player_1_id),
            select_card(card_player_2_id),
        )

    response2 = client.put(
        "/game/1/trade-card", json={"playerID": game_event.player2.id, "cardID": 800}
    )

    assert response2.status_code == 400
    assert response2.json() == {"detail": "Card not found"}

    with db_session:
        game, game_event, cards_player_1, cards_player_2 = get_game_and_cards()
        assert_game_state(
            game,
            game_event,
            is_completed=False,
            player1=game_event.player1,
            player2=game_event.player2,
            card1=select_card(card_player_1_id),
            card2=None,
            action="trade",
            current_player=game_event.player2.id,
        )

        assert_game_cards(
            game,
            game_event,
            select_card(card_player_1_id),
            select_card(card_player_2_id),
        )

    response2 = client.put(
        "/game/1/trade-card", json={"playerID": player2_id, "cardID": card_player_2_id}
    )

    assert response2.status_code == 200

    with db_session:
        game, game_event, cards_player_1, cards_player_2 = get_game_and_cards()
        next_position = next_player(game, game_event)

        assert_game_state(
            game,
            game_event,
            is_completed=True,
            player1=game_event.player1,
            player2=game_event.player2,
            card1=select_card(card_player_1_id),
            card2=select_card(card_player_2_id),
            action="draw",
            current_player=next_position,
            is_successful=True,
        )

        assert_game_cards(
            game,
            game_event,
            select_card(card_player_2_id),
            select_card(card_player_1_id),
        )


def test_trade_in_invalid_turn_state(db_game_creation_with_trade_event):
    player1_id = None
    player2_id = None
    card_player_1_id = None
    card_player_2_id = None
    with db_session:
        game, game_event, cards_player_1, cards_player_2 = get_game_and_cards()

        player1_id = game_event.player1.id
        player2_id = game_event.player2.id

        card_player_1_id = cards_player_1[1].id
        card_player_2_id = cards_player_2[3].id

    response1 = client.put(
        "/game/1/trade-card", json={"playerID": player2_id, "cardID": card_player_2_id}
    )

    assert response1.status_code == 403
    assert response1.json() == {
        "detail": "Player not has permission to execute this action"
    }

    with db_session:
        game, game_event, cards_player_1, cards_player_2 = get_game_and_cards()

        assert_game_state(
            game,
            game_event,
            is_completed=False,
            player1=game_event.player1,
            player2=game_event.player2,
            card1=None,
            card2=None,
            action="trade",
            current_player=game_event.player1.id,
        )

        assert_game_cards(
            game,
            game_event,
            select_card(card_player_1_id),
            select_card(card_player_2_id),
        )

        game.current_action = "action"

    response1 = client.put(
        "/game/1/trade-card", json={"playerID": player1_id, "cardID": card_player_1_id}
    )

    assert response1.status_code == 403
    assert response1.json() == {
        "detail": "Player not has permission to execute this action"
    }

    with db_session:
        game, game_event, cards_player_1, cards_player_2 = get_game_and_cards()

        assert_game_state(
            game,
            game_event,
            is_completed=False,
            player1=game_event.player1,
            player2=game_event.player2,
            card1=None,
            card2=None,
            action="action",
            current_player=game_event.player1.id,
        )

        assert_game_cards(
            game,
            game_event,
            select_card(card_player_1_id),
            select_card(card_player_2_id),
        )

        game.current_action = "trade"

    response1 = client.put(
        "/game/1/trade-card", json={"playerID": player1_id, "cardID": card_player_1_id}
    )

    assert response1.status_code == 200

    with db_session:
        game, game_event, cards_player_1, cards_player_2 = get_game_and_cards()

        assert_game_state(
            game,
            game_event,
            is_completed=False,
            player1=game_event.player1,
            player2=game_event.player2,
            card1=select_card(card_player_1_id),
            card2=None,
            action="defense",
            current_player=game_event.player2.id,
        )

        assert_game_cards(
            game,
            game_event,
            select_card(card_player_1_id),
            select_card(card_player_2_id),
        )

    response2 = client.put(
        "/game/1/defend-card", json={"playerID": player2_id, "cardID": -1}
    )

    assert response2.status_code == 200

    with db_session:
        game, game_event, cards_player_1, cards_player_2 = get_game_and_cards()

        assert_game_state(
            game,
            game_event,
            is_completed=False,
            player1=game_event.player1,
            player2=game_event.player2,
            card1=select_card(card_player_1_id),
            card2=None,
            action="trade",
            current_player=game_event.player2.id,
        )

        assert_game_cards(
            game,
            game_event,
            select_card(card_player_1_id),
            select_card(card_player_2_id),
        )

    response3 = client.put(
        "/game/1/trade-card", json={"playerID": player1_id, "cardID": card_player_1_id}
    )

    assert response3.status_code == 403
    assert response3.json() == {
        "detail": "Player not has permission to execute this action"
    }

    with db_session:
        game, game_event, cards_player_1, cards_player_2 = get_game_and_cards()

        assert_game_state(
            game,
            game_event,
            is_completed=False,
            player1=game_event.player1,
            player2=game_event.player2,
            card1=select_card(card_player_1_id),
            card2=None,
            action="trade",
            current_player=game_event.player2.id,
        )

        assert_game_cards(
            game,
            game_event,
            select_card(card_player_1_id),
            select_card(card_player_2_id),
        )

    response2 = client.put(
        "/game/1/trade-card", json={"playerID": player2_id, "cardID": card_player_2_id}
    )

    assert response2.status_code == 200

    next_position = None
    with db_session:
        game, game_event, cards_player_1, cards_player_2 = get_game_and_cards()
        next_position = next_player(game, game_event)

        assert_game_state(
            game,
            game_event,
            is_completed=True,
            player1=game_event.player1,
            player2=game_event.player2,
            card1=select_card(card_player_1_id),
            card2=select_card(card_player_2_id),
            action="draw",
            current_player=next_position,
            is_successful=True,
        )

        assert_game_cards(
            game,
            game_event,
            select_card(card_player_2_id),
            select_card(card_player_1_id),
        )


def test_use_no_gracias_as_tradeable_card(db_game_creation_with_trade_event_2):
    player1_id = None
    player2_id = None
    card_player_1_id = None
    card_player_2_id = None
    with db_session:
        game = Game.get(id=1)
        players = list(select(p for p in game.players))
        delete(e for e in game.events)
        game.events.create(type="trade", player1=players[0], player2=players[4])
        game, game_event, cards_player_1, cards_player_2 = get_game_and_cards()

        player1_id = game_event.player1.id
        player2_id = game_event.player2.id
        card_player_1_id = cards_player_1[1].id
        card_player_2_id = cards_player_2[3].id

    response1 = client.put(
        "/game/1/trade-card", json={"playerID": player1_id, "cardID": card_player_1_id}
    )

    assert response1.status_code == 200

    with db_session:
        game, game_event, cards_player_1, cards_player_2 = get_game_and_cards()

        assert_game_state(
            game,
            game_event,
            is_completed=False,
            player1=game_event.player1,
            player2=game_event.player2,
            card1=select_card(card_player_1_id),
            card2=None,
            action="defense",
            current_player=game_event.player2.id,
        )

        assert_game_cards(
            game,
            game_event,
            select_card(card_player_1_id),
            select_card(card_player_2_id),
        )

    response2 = client.put(
        "/game/1/defend-card", json={"playerID": player2_id, "cardID": -1}
    )

    assert response2.status_code == 200

    with db_session:
        game, game_event, cards_player_1, cards_player_2 = get_game_and_cards()

        assert_game_state(
            game,
            game_event,
            is_completed=False,
            player1=game_event.player1,
            player2=game_event.player2,
            card1=select_card(card_player_1_id),
            card2=None,
            action="trade",
            current_player=game_event.player2.id,
        )

        assert_game_cards(
            game,
            game_event,
            select_card(card_player_1_id),
            select_card(card_player_2_id),
        )

    response3 = client.put(
        "/game/1/trade-card", json={"playerID": player2_id, "cardID": card_player_2_id}
    )

    assert response3.status_code == 200

    with db_session:
        game, game_event, cards_player_1, cards_player_2 = get_game_and_cards()
        next_position = next_player(game, game_event)

        assert_game_state(
            game,
            game_event,
            is_completed=True,
            player1=game_event.player1,
            player2=game_event.player2,
            card1=select_card(card_player_1_id),
            card2=select_card(card_player_2_id),
            action="draw",
            current_player=next_position,
            is_successful=True,
        )

        assert_game_cards(
            game,
            game_event,
            select_card(card_player_2_id),
            select_card(card_player_1_id),
        )


def test_succesful_contagion(db_game_creation_with_trade_event_2):
    player1_id = None
    player2_id = None
    card_player_1_id = None
    card_player_2_id = None
    with db_session:
        game = Game.get(id=1)
        players = list(select(p for p in game.players))
        delete(e for e in game.events)
        game.events.create(type="trade", player1=players[1], player2=players[4])
        game, game_event, cards_player_1, cards_player_2 = get_game_and_cards()

        player1_id = game_event.player1.id
        player2_id = game_event.player2.id

        card_player_1_id = cards_player_1[0].id
        card_player_2_id = cards_player_2[1].id

        game.current_player = game_event.player1.id
        commit()

    response1 = client.put(
        "/game/1/trade-card", json={"playerID": player1_id, "cardID": card_player_1_id}
    )

    assert response1.status_code == 200

    with db_session:
        game, game_event, cards_player_1, cards_player_2 = get_game_and_cards()

        assert_game_state(
            game,
            game_event,
            is_completed=False,
            player1=game_event.player1,
            player2=game_event.player2,
            card1=select_card(card_player_1_id),
            card2=None,
            action="defense",
            current_player=game_event.player2.id,
        )

        assert_game_cards(
            game,
            game_event,
            select_card(card_player_1_id),
            select_card(card_player_2_id),
        )

    response2 = client.put(
        "/game/1/defend-card", json={"playerID": player2_id, "cardID": -1}
    )

    assert response2.status_code == 200

    with db_session:
        game, game_event, cards_player_1, cards_player_2 = get_game_and_cards()

        assert_game_state(
            game,
            game_event,
            is_completed=False,
            player1=game_event.player1,
            player2=game_event.player2,
            card1=select_card(card_player_1_id),
            card2=None,
            action="trade",
            current_player=game_event.player2.id,
        )

        assert_game_cards(
            game,
            game_event,
            select_card(card_player_1_id),
            select_card(card_player_2_id),
        )

    response3 = client.put(
        "/game/1/trade-card", json={"playerID": player2_id, "cardID": card_player_2_id}
    )

    assert response3.status_code == 200

    with db_session:
        game, game_event, cards_player_1, cards_player_2 = get_game_and_cards()

        assert (
            select(p for p in game.players if p.id == player2_id).first().role
            == "infected"
        )

        assert_game_state(
            game,
            game_event,
            is_completed=True,
            player1=game_event.player1,
            player2=game_event.player2,
            card1=select_card(card_player_1_id),
            card2=select_card(card_player_2_id),
            action="draw",
            current_player=players[3].id,
            is_successful=True,
        )

        assert_game_cards(
            game,
            game_event,
            select_card(card_player_2_id),
            select_card(card_player_1_id),
        )


def test_try_trade_card_la_cosa_infeccion(db_game_creation_with_trade_event_2):
    player1_id = None
    card_player_1_id = None

    # infected to human trade card Infeccion
    with db_session:
        game = Game.get(id=1)
        players = select(p for p in game.players)[:]
        game.events.create(type="trade", player1=players[3], player2=players[4])
        game, game_event, cards_player_1, cards_player_2 = get_game_and_cards()

        player1_id = game_event.player1.id
        card_player_1_id = cards_player_1[0].id
        cards_player_2[1].id

    response1 = client.put(
        "/game/1/trade-card", json={"playerID": player1_id, "cardID": card_player_1_id}
    )

    assert response1.status_code == 403

    # human to infected trade card Infeccion
    with db_session:
        game = Game.get(id=1)
        delete(e for e in game.events)
        commit()
        players = select(p for p in game.players)[:]
        game.events.create(type="trade", player1=players[4], player2=players[3])
        game, game_event, cards_player_1, cards_player_2 = get_game_and_cards()

        player1_id = game_event.player1.id
        card_player_1_id = cards_player_1[1].id
        cards_player_2[0].id

    response1 = client.put(
        "/game/1/trade-card", json={"playerID": player1_id, "cardID": card_player_1_id}
    )

    assert response1.status_code == 403

    # thing try to trade card thing
    with db_session:
        game = Game.get(id=1)
        delete(e for e in game.events)
        commit()
        players = select(p for p in game.players)[:]
        game.events.create(type="trade", player1=players[1], player2=players[0])
        game, game_event, cards_player_1, cards_player_2 = get_game_and_cards()

        player1_id = game_event.player1.id
        card_player_1_id = cards_player_1[1].id
        cards_player_2[1].id

    response1 = client.put(
        "/game/1/trade-card", json={"playerID": player1_id, "cardID": card_player_1_id}
    )

    assert response1.status_code == 403


def test_try_infected_to_the_thing_send_card(db_game_creation_with_trade_event_3):
    player1_id = None
    player2_id = None
    card_player_1_id = None
    card_player_2_id = None

    # infected to thing trade card Infeccion
    with db_session:
        game = Game.get(id=1)
        players = select(p for p in game.players)[:]
        game.events.create(type="trade", player1=players[0], player2=players[1])
        game, game_event, cards_player_1, cards_player_2 = get_game_and_cards()

        player1_id = game_event.player1.id
        player2_id = game_event.player2.id

        card_player_1_id = cards_player_1[0].id
        card_player_2_id = cards_player_2[2].id

        game.current_player = game_event.player1.id

    response1 = client.put(
        "/game/1/trade-card", json={"playerID": player1_id, "cardID": card_player_1_id}
    )

    assert response1.status_code == 200

    with db_session:
        game, game_event, cards_player_1, cards_player_2 = get_game_and_cards()

        assert_game_state(
            game,
            game_event,
            is_completed=False,
            player1=game_event.player1,
            player2=game_event.player2,
            card1=select_card(card_player_1_id),
            card2=None,
            action="defense",
            current_player=game_event.player2.id,
        )

        assert_game_cards(
            game,
            game_event,
            select_card(card_player_1_id),
            select_card(card_player_2_id),
        )

    response2 = client.put(
        "/game/1/defend-card", json={"playerID": player2_id, "cardID": -1}
    )

    assert response2.status_code == 200

    with db_session:
        game, game_event, cards_player_1, cards_player_2 = get_game_and_cards()

        assert_game_state(
            game,
            game_event,
            is_completed=False,
            player1=game_event.player1,
            player2=game_event.player2,
            card1=select_card(card_player_1_id),
            card2=None,
            action="trade",
            current_player=game_event.player2.id,
        )

        assert_game_cards(
            game,
            game_event,
            select_card(card_player_1_id),
            select_card(card_player_2_id),
        )

    response3 = client.put(
        "/game/1/trade-card", json={"playerID": player2_id, "cardID": card_player_2_id}
    )

    assert response3.status_code == 200

    with db_session:
        game, game_event, cards_player_1, cards_player_2 = get_game_and_cards()

        next_player_id = next_player(game, game_event)

        assert_game_state(
            game,
            game_event,
            is_completed=True,
            player1=game_event.player1,
            player2=game_event.player2,
            card1=select_card(card_player_1_id),
            card2=select_card(card_player_2_id),
            action="draw",
            current_player=next_player_id,
            is_successful=True,
        )

        assert_game_cards(
            game,
            game_event,
            select_card(card_player_2_id),
            select_card(card_player_1_id),
        )

    # thing to infected trade card Infeccion
    with db_session:
        game = Game.get(id=1)
        delete(e for e in game.events)
        commit()
        players = select(p for p in game.players)[:]
        game.events.create(type="trade", player1=players[1], player2=players[0])
        game, game_event, cards_player_1, cards_player_2 = get_game_and_cards()

        player1_id = game_event.player1.id
        player2_id = game_event.player2.id

        card_player_1_id = cards_player_1[0].id
        card_player_2_id = cards_player_2[0].id

    response1 = client.put(
        "/game/1/trade-card", json={"playerID": player1_id, "cardID": card_player_1_id}
    )

    assert response1.status_code == 403


def test_get_defense_cards_info(get_defend_trade_card_game_creation):
    player1_id = None
    player2_id = None
    card_player_1_id = None
    card_player_2_id = None

    with db_session:
        game = Game.get(id=1)
        players = select(p for p in game.players)[:]
        game.events.create(
            type="trade", player1=players[0], player2=players[1], card1=None, card2=None
        )

        game, game_event, cards_player_1, cards_player_2 = get_game_and_cards()

        player1_id = game_event.player1.id
        player2_id = game_event.player2.id

        card_player_1_id = cards_player_1[1].id
        card_player_2_id = cards_player_2[1].id

        game.current_action = "trade"
        game.current_player = game_event.player1.id

    response = client.get(f"/player/{player1_id}/cards-defend/-1")

    assert response.status_code == 200

    assert response.json() == {"cards": []}

    response1 = client.put(
        "/game/1/trade-card", json={"playerID": player1_id, "cardID": card_player_1_id}
    )

    assert response1.status_code == 200

    with db_session:
        game, game_event, cards_player_1, cards_player_2 = get_game_and_cards()

        assert_game_state(
            game,
            game_event,
            is_completed=False,
            player1=game_event.player1,
            player2=game_event.player2,
            card1=select_card(card_player_1_id),
            card2=None,
            action="defense",
            current_player=game_event.player2.id,
        )

    response = client.get(f"/player/{player2_id}/cards-defend/-1")

    assert response.status_code == 200

    assert len(response.json()["cards"]) == 4

    response2 = client.put(
        "/game/1/defend-card", json={"playerID": player2_id, "cardID": -1}
    )

    assert response2.status_code == 200

    with db_session:
        game, game_event, cards_player_1, cards_player_2 = get_game_and_cards()

        assert_game_state(
            game,
            game_event,
            is_completed=False,
            player1=game_event.player1,
            player2=game_event.player2,
            card1=select_card(card_player_1_id),
            card2=None,
            action="trade",
            current_player=game_event.player2.id,
        )

        assert_game_cards(
            game,
            game_event,
            select_card(card_player_1_id),
            select_card(card_player_2_id),
        )

    response3 = client.put(
        "/game/1/trade-card", json={"playerID": player2_id, "cardID": card_player_2_id}
    )

    assert response3.status_code == 200

    with db_session:
        game, game_event, cards_player_1, cards_player_2 = get_game_and_cards()
        next_position = next_player(game, game_event)

        assert_game_state(
            game,
            game_event,
            is_completed=True,
            player1=game_event.player1,
            player2=game_event.player2,
            card1=select_card(card_player_1_id),
            card2=select_card(card_player_2_id),
            action="draw",
            current_player=next_position,
            is_successful=True,
        )

        assert_game_cards(
            game,
            game_event,
            select_card(card_player_2_id),
            select_card(card_player_1_id),
        )
