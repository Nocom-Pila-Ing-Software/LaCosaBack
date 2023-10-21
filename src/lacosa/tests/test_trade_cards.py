from main import app
from fastapi.testclient import TestClient
from models import Game
from pony.orm import db_session, select, commit
import pytest
from .game_fixtures import db_game_creation_with_trade_event

client = TestClient(app)


def next_player(game, game_event):
    next_player = game.players.select(
        lambda p: p.position == game_event.player1.position + 1).first()
    if next_player is None:
        next_player = game.players.select(
            lambda p: p.position == 1).first()
    return next_player.id


def get_game_and_cards():
    game = Game.get(id=1)
    game_event = select(e for e in game.events).first()
    cards_player_1 = select(e for e in game_event.player1.cards)[:]
    cards_player_2 = select(e for e in game_event.player2.cards)[:]
    return game, game_event, cards_player_1, cards_player_2


def select_card(game, card_id):
    return select(c for c in game.cards if c.id == card_id).first()


def assert_game_state(game, game_event, is_completed, player1, player2, card1, card2, action, current_player, is_successful=False):
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
        "/game/1/trade-card", json={"playerID": player1_id, "cardID": card_player_1_id})

    assert response1.status_code == 200

    with db_session:
        game, game_event, cards_player_1, cards_player_2 = get_game_and_cards()

        assert_game_state(game, game_event, is_completed=False, player1=game_event.player1,
                          player2=game_event.player2, card1=select_card(game, card_player_1_id), card2=None, action="trade", current_player=game_event.player2.id)

        assert_game_cards(game, game_event, select_card(
            game, card_player_1_id), select_card(game, card_player_2_id))

    response2 = client.put(
        "/game/1/trade-card", json={"playerID": player2_id, "cardID": card_player_2_id})

    assert response2.status_code == 200

    with db_session:
        game, game_event, cards_player_1, cards_player_2 = get_game_and_cards()
        next_position = next_player(game, game_event)

        assert_game_state(game, game_event, is_completed=True, player1=game_event.player1,
                          player2=game_event.player2, card1=select_card(game, card_player_1_id), card2=select_card(game, card_player_2_id), action="draw", current_player=next_position, is_successful=True)

        assert_game_cards(game, game_event, select_card(
            game, card_player_2_id), select_card(game, card_player_1_id))


def test_unsuccessfull_trade(db_game_creation_with_trade_event):
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
        "/game/1/trade-card", json={"playerID": player1_id, "cardID": card_player_1_id})

    assert response1.status_code == 200

    with db_session:
        game, game_event, cards_player_1, cards_player_2 = get_game_and_cards()

        assert_game_state(game, game_event, is_completed=False, player1=game_event.player1,
                          player2=game_event.player2, card1=select_card(game, card_player_1_id), card2=None, action="trade", current_player=game_event.player2.id)

        assert_game_cards(game, game_event, select_card(
            game, card_player_1_id), select_card(game, card_player_2_id))

    response2 = client.put(
        "/game/1/defend-card", json={"playerID": player2_id, "cardID": card_player_2_id})

    assert response2.status_code == 200

    with db_session:
        game, game_event, cards_player_1, cards_player_2 = get_game_and_cards()

        next_position = next_player(game, game_event)

        assert_game_state(game, game_event, is_completed=True, player1=game_event.player1,
                          player2=game_event.player2, card1=select_card(game, card_player_1_id), card2=select_card(game, card_player_2_id), action="draw", current_player=next_position, is_successful=False)

        assert select_card(game, card_player_1_id) in cards_player_1
        assert select_card(game, card_player_1_id) not in cards_player_2
        assert select_card(game, card_player_2_id) not in cards_player_2
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
        "/game/2/trade-card", json={"playerID": player1_id, "cardID": card_player_1_id})

    assert response1.status_code == 404
    assert response1.json() == {"detail": "Game not found"}

    with db_session:
        game, game_event, cards_player_1, cards_player_2 = get_game_and_cards()
        assert_game_state(game, game_event, is_completed=False, player1=game_event.player1,
                          player2=game_event.player2, card1=None, card2=None, action="trade", current_player=game_event.player1.id)

        assert_game_cards(game, game_event, select_card(
            game, card_player_1_id), select_card(game, card_player_2_id))

    response1 = client.put(
        "/game/1/trade-card", json={"playerID": player1_id, "cardID": card_player_1_id})

    assert response1.status_code == 200

    with db_session:
        game, game_event, cards_player_1, cards_player_2 = get_game_and_cards()

        assert_game_state(game, game_event, is_completed=False, player1=game_event.player1,
                          player2=game_event.player2, card1=select_card(game, card_player_1_id), card2=None, action="trade", current_player=game_event.player2.id)

        assert_game_cards(game, game_event, select_card(
            game, card_player_1_id), select_card(game, card_player_2_id))

    response2 = client.put(
        "/game/2/trade-card", json={"playerID": player2_id, "cardID": card_player_2_id})

    assert response2.status_code == 404
    assert response2.json() == {"detail": "Game not found"}

    with db_session:
        game, game_event, cards_player_1, cards_player_2 = get_game_and_cards()

        assert_game_state(game, game_event, is_completed=False, player1=game_event.player1,
                          player2=game_event.player2, card1=select_card(game, card_player_1_id), card2=None, action="trade", current_player=game_event.player2.id)

        assert_game_cards(game, game_event, select_card(
            game, card_player_1_id), select_card(game, card_player_2_id))


def test_trade_with_invalid_player_id(db_game_creation_with_trade_event):
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
        "/game/1/trade-card", json={"playerID": 30000, "cardID": card_player_1_id})

    assert response1.status_code == 400
    assert response1.json() == {"detail": "Player not found"}

    with db_session:
        game, game_event, cards_player_1, cards_player_2 = get_game_and_cards()

        assert_game_state(game, game_event, is_completed=False, player1=game_event.player1,
                          player2=game_event.player2, card1=None, card2=None, action="trade", current_player=game_event.player1.id)

        assert_game_cards(game, game_event, select_card(
            game, card_player_1_id), select_card(game, card_player_2_id))

    response1 = client.put(
        "/game/1/trade-card", json={"playerID": player1_id, "cardID": card_player_1_id})

    assert response1.status_code == 200

    with db_session:
        game, game_event, cards_player_1, cards_player_2 = get_game_and_cards()

        assert_game_state(game, game_event, is_completed=False, player1=game_event.player1,
                          player2=game_event.player2, card1=select_card(game, card_player_1_id), card2=None, action="trade", current_player=game_event.player2.id)

        assert_game_cards(game, game_event, select_card(
            game, card_player_1_id), select_card(game, card_player_2_id))

    response2 = client.put(
        "/game/1/trade-card", json={"playerID": 8998, "cardID": card_player_2_id})

    assert response2.status_code == 400
    assert response2.json() == {"detail": "Player not found"}

    with db_session:
        game, game_event, cards_player_1, cards_player_2 = get_game_and_cards()
        assert_game_state(game, game_event, is_completed=False, player1=game_event.player1,
                          player2=game_event.player2, card1=select_card(game, card_player_1_id), card2=None, action="trade", current_player=game_event.player2.id)

        assert_game_cards(game, game_event, select_card(
            game, card_player_1_id), select_card(game, card_player_2_id))


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
        "/game/1/trade-card", json={"playerID": player1_id, "cardID": card_player_2_id})

    assert response1.status_code == 400
    assert response1.json() == {"detail": "Player does not have that card"}

    with db_session:
        game, game_event, cards_player_1, cards_player_2 = get_game_and_cards()

        assert_game_state(game, game_event, is_completed=False, player1=game_event.player1,
                          player2=game_event.player2, card1=None, card2=None, action="trade", current_player=game_event.player1.id)

        assert_game_cards(game, game_event, select_card(
            game, card_player_1_id), select_card(game, card_player_2_id))

    response1 = client.put(
        "/game/1/trade-card", json={"playerID": player1_id, "cardID": card_player_1_id})

    assert response1.status_code == 200

    with db_session:
        game, game_event, cards_player_1, cards_player_2 = get_game_and_cards()

        assert_game_state(game, game_event, is_completed=False, player1=game_event.player1,
                          player2=game_event.player2, card1=select_card(game, card_player_1_id), card2=None, action="trade", current_player=game_event.player2.id)

        assert_game_cards(game, game_event, select_card(
            game, card_player_1_id), select_card(game, card_player_2_id))

    response2 = client.put(
        "/game/1/trade-card", json={"playerID": player2_id, "cardID": card_player_1_id})

    assert response2.status_code == 400
    assert response2.json() == {"detail": "Player does not have that card"}

    with db_session:
        game, game_event, cards_player_1, cards_player_2 = get_game_and_cards()

        assert_game_state(game, game_event, is_completed=False, player1=game_event.player1,
                          player2=game_event.player2, card1=select_card(
                              game, card_player_1_id), card2=None, action="trade", current_player=game_event.player2.id)

        assert_game_cards(game, game_event, select_card(
            game, card_player_1_id), select_card(game, card_player_2_id))

    response2 = client.put(
        "/game/1/trade-card", json={"playerID": game_event.player2.id, "cardID": 800})

    assert response2.status_code == 400
    assert response2.json() == {"detail": "Card not found"}

    with db_session:
        game, game_event, cards_player_1, cards_player_2 = get_game_and_cards()
        assert_game_state(game, game_event, is_completed=False, player1=game_event.player1,
                          player2=game_event.player2, card1=select_card(
                              game, card_player_1_id), card2=None, action="trade", current_player=game_event.player2.id)

        assert_game_cards(game, game_event, select_card(
            game, card_player_1_id), select_card(game, card_player_2_id))

    response2 = client.put(
        "/game/1/trade-card", json={"playerID": player2_id, "cardID": card_player_2_id})

    assert response2.status_code == 200

    with db_session:
        game, game_event, cards_player_1, cards_player_2 = get_game_and_cards()
        next_position = next_player(game, game_event)

        assert_game_state(game, game_event, is_completed=True, player1=game_event.player1,
                          player2=game_event.player2, card1=select_card(game, card_player_1_id), card2=select_card(game, card_player_2_id), action="draw", current_player=next_position, is_successful=True)

        assert_game_cards(game, game_event, select_card(
            game, card_player_2_id), select_card(game, card_player_1_id))


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

        # print all the events in the game
        for event in game.events:
            print(event.card1, event.card2, event.is_completed)

    response1 = client.put(
        "/game/1/trade-card", json={"playerID": player2_id, "cardID": card_player_2_id})

    assert response1.status_code == 403
    assert response1.json() == {
        "detail": "Player not has permission to execute this action"}

    with db_session:
        game, game_event, cards_player_1, cards_player_2 = get_game_and_cards()

        assert_game_state(game, game_event, is_completed=False, player1=game_event.player1,
                          player2=game_event.player2, card1=None, card2=None, action="trade", current_player=game_event.player1.id)

        assert_game_cards(game, game_event, select_card(
            game, card_player_1_id), select_card(game, card_player_2_id))

        game.current_action = "action"

    response1 = client.put(
        "/game/1/trade-card", json={"playerID": player1_id, "cardID": card_player_1_id})

    assert response1.status_code == 403
    assert response1.json() == {
        "detail": "Player not has permission to execute this action"}

    with db_session:
        game, game_event, cards_player_1, cards_player_2 = get_game_and_cards()

        assert_game_state(game, game_event, is_completed=False, player1=game_event.player1,
                          player2=game_event.player2, card1=None, card2=None, action="action", current_player=game_event.player1.id)

        assert_game_cards(game, game_event, select_card(
            game, card_player_1_id), select_card(game, card_player_2_id))

        game.current_action = "trade"

    response1 = client.put(
        "/game/1/trade-card", json={"playerID": player1_id, "cardID": card_player_1_id})

    assert response1.status_code == 200

    with db_session:
        game, game_event, cards_player_1, cards_player_2 = get_game_and_cards()

        assert_game_state(game, game_event, is_completed=False, player1=game_event.player1,
                          player2=game_event.player2, card1=select_card(game, card_player_1_id), card2=None, action="trade", current_player=game_event.player2.id)

        assert_game_cards(game, game_event, select_card(
            game, card_player_1_id), select_card(game, card_player_2_id))

    response2 = client.put(
        "/game/1/trade-card", json={"playerID": player1_id, "cardID": card_player_1_id})

    assert response2.status_code == 403
    assert response2.json() == {
        "detail": "Player not has permission to execute this action"}

    with db_session:
        game, game_event, cards_player_1, cards_player_2 = get_game_and_cards()

        assert_game_state(game, game_event, is_completed=False, player1=game_event.player1,
                          player2=game_event.player2, card1=select_card(game, card_player_1_id), card2=None, action="trade", current_player=game_event.player2.id)

        assert_game_cards(game, game_event, select_card(
            game, card_player_1_id), select_card(game, card_player_2_id))

    response2 = client.put(
        "/game/1/trade-card", json={"playerID": player2_id, "cardID": card_player_2_id})

    assert response2.status_code == 200

    next_position = None
    with db_session:
        game, game_event, cards_player_1, cards_player_2 = get_game_and_cards()
        next_position = next_player(game, game_event)

        assert_game_state(game, game_event, is_completed=True, player1=game_event.player1, player2=game_event.player2, card1=select_card(
            game, card_player_1_id), card2=select_card(game, card_player_2_id), action="draw", current_player=next_position, is_successful=True)

        assert_game_cards(game, game_event, select_card(
            game, card_player_2_id), select_card(game, card_player_1_id))
