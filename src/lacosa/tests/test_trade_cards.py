from main import app
from fastapi.testclient import TestClient
from models import Game
from pony.orm import db_session, select
import pytest
from .game_fixtures import db_game_creation_with_trade_event

client = TestClient(app)


def get_game_and_cards():
    game = Game.get(id=1)
    game_event = select(e for e in game.events).first()
    cards_player_1 = select(e for e in game_event.player1.cards)[:]
    cards_player_2 = select(e for e in game_event.player2.cards)[:]
    return game, game_event, cards_player_1, cards_player_2


def assert_game_state(game, game_event, is_completed, player1, player2, card1, card2, action, current_player, is_successful=False):
    assert game_event.is_completed == is_completed
    assert game_event.is_successful == is_successful

    assert game_event.card1 == card1
    assert game_event.card2 == card2

    assert game.current_action == action
    assert game.current_player == current_player


def assert_game_cards(game, game_event, card_player_1, card_player_2):
    assert len(game.players.get(id=game_event.player1.id).cards) == 4
    assert len(game.players.get(id=game_event.player2.id).cards) == 4

    assert card_player_1 in game.players.get(
        id=game_event.player1.id).cards
    assert card_player_2 in game.players.get(
        id=game_event.player2.id).cards

    assert card_player_1 not in game.players.get(
        id=game_event.player2.id).cards
    assert card_player_2 not in game.players.get(
        id=game_event.player1.id).cards


def test_successfull_trade(db_game_creation_with_trade_event):
    with db_session:
        game, game_event, cards_player_1, cards_player_2 = get_game_and_cards()
        card_player_1 = cards_player_1[1]
        card_player_2 = cards_player_2[3]

        response1 = client.put(
            "/game/1/trade_card", json={"playerID": game_event.player1.id, "cardID": card_player_1.id})

        assert response1.status_code == 200

        assert_game_state(game, game_event, is_completed=False, player1=game_event.player1,
                          player2=game_event.player2, card1=card_player_1, card2=None, action="trade", current_player=game_event.player2.id)

        assert_game_cards(game, game_event, card_player_1, card_player_2)

        response2 = client.put(
            "/game/1/trade_card", json={"playerID": game_event.player2.id, "cardID": card_player_2.id})

        next_position = (game.players.get(
            id=game_event.player1.id).position+1) % len(game.players)

        assert_game_state(game, game_event, is_completed=True, player1=game_event.player1,
                          player2=game_event.player2, card1=card_player_1, card2=card_player_2, action="draw", current_player=next_position, is_successful=True)

        assert response2.status_code == 200

        assert_game_cards(game, game_event, card_player_2, card_player_1)


def test_unsuccessfull_trade(db_game_creation_with_trade_event):
    with db_session:
        game, game_event, cards_player_1, cards_player_2 = get_game_and_cards()
        card_player_1 = cards_player_1[1]
        card_player_2 = cards_player_2[3]

        response1 = client.put(
            "/game/1/trade_card", json={"playerID": game_event.player1.id, "cardID": card_player_1.id})

        assert response1.status_code == 200

        assert_game_state(game, game_event, is_completed=False, player1=game_event.player1,
                          player2=game_event.player2, card1=card_player_1, card2=None, action="trade", current_player=game_event.player2.id)

        assert_game_cards(game, game_event, card_player_1, card_player_2)

        response2 = client.put(
            "/game/1/defend-card", json={"playerID": game_event.player2.id, "cardID": card_player_2.id})

        assert response2.status_code == 200

        next_position = (game.players.get(
            id=game_event.player1.id).position+1) % len(game.players)

        assert_game_state(game, game_event, is_completed=True, player1=game_event.player1,
                          player2=game_event.player2, card1=card_player_1, card2=card_player_2, action="draw", current_player=next_position, is_successful=False)

        assert card_player_1 in game.players.get(
            id=game_event.player1.id).cards
        assert card_player_1 not in game.players.get(
            id=game_event.player2.id).cards
        assert card_player_2 not in game.players.get(
            id=game_event.player2.id).cards

        assert len(game.players.get(id=game_event.player1.id).cards) == 4
        assert len(game.players.get(id=game_event.player2.id).cards) == 4


def test_trade_with_invalid_room_id(db_game_creation_with_trade_event):
    with db_session:
        game, game_event, cards_player_1, cards_player_2 = get_game_and_cards()
        card_player_1 = cards_player_1[1]
        card_player_2 = cards_player_2[3]

        response1 = client.put(
            "/game/2/trade_card", json={"playerID": game_event.player1.id, "cardID": card_player_1.id})

        assert response1.status_code == 404
        assert response1.json() == {"detail": "Game not found"}

        assert_game_state(game, game_event, is_completed=False, player1=game_event.player1,
                          player2=game_event.player2, card1=None, card2=None, action="trade", current_player=game_event.player1.id)

        assert_game_cards(game, game_event, card_player_1, card_player_2)

        response1 = client.put(
            "/game/1/trade_card", json={"playerID": game_event.player1.id, "cardID": card_player_1.id})

        assert response1.status_code == 200

        assert_game_state(game, game_event, is_completed=False, player1=game_event.player1,
                          player2=game_event.player2, card1=card_player_1, card2=None, action="trade", current_player=game_event.player2.id)

        assert_game_cards(game, game_event, card_player_1, card_player_2)

        response2 = client.put(
            "/game/2/trade_card", json={"playerID": game_event.player2.id, "cardID": card_player_2.id})

        assert response2.status_code == 404
        assert response2.json() == {"detail": "Game not found"}

        assert_game_state(game, game_event, is_completed=False, player1=game_event.player1,
                          player2=game_event.player2, card1=card_player_1, card2=None, action="trade", current_player=game_event.player2.id)

        assert_game_cards(game, game_event, card_player_1, card_player_2)


def test_trade_with_invalid_player_id(db_game_creation_with_trade_event):
    with db_session:
        game, game_event, cards_player_1, cards_player_2 = get_game_and_cards()
        card_player_1 = cards_player_1[1]
        card_player_2 = cards_player_2[3]

        response1 = client.put(
            "/game/1/trade_card", json={"playerID": 30000, "cardID": card_player_1.id})

        assert response1.status_code == 400
        assert response1.json() == {"detail": "Player not found"}

        assert_game_state(game, game_event, is_completed=False, player1=game_event.player1,
                          player2=game_event.player2, card1=None, card2=None, action="trade", current_player=game_event.player1.id)

        assert_game_cards(game, game_event, card_player_1, card_player_2)

        response1 = client.put(
            "/game/1/trade_card", json={"playerID": game_event.player1.id, "cardID": card_player_1.id})

        assert response1.status_code == 200

        assert_game_state(game, game_event, is_completed=False, player1=game_event.player1,
                          player2=game_event.player2, card1=card_player_1, card2=None, action="trade", current_player=game_event.player2.id)

        assert_game_cards(game, game_event, card_player_1, card_player_2)

        response2 = client.put(
            "/game/1/trade_card", json={"playerID": 8998, "cardID": card_player_2.id})

        assert response2.status_code == 400
        assert response1.json() == {"detail": "Player not found"}

        assert_game_state(game, game_event, is_completed=False, player1=game_event.player1,
                          player2=game_event.player2, card1=card_player_1, card2=None, action="trade", current_player=game_event.player2.id)

        assert_game_cards(game, game_event, card_player_1, card_player_2)


def test_trade_with_card_not_in_hand(db_game_creation_with_trade_event):
    with db_session:
        game, game_event, cards_player_1, cards_player_2 = get_game_and_cards()
        card_player_1 = cards_player_1[1]
        card_player_2 = cards_player_2[3]

        response1 = client.put(
            "/game/1/trade_card", json={"playerID": game_event.player1.id, "cardID": card_player_2.id})

        assert response1.status_code == 400
        assert response1.json() == {"detail": "Player doesn't have that card"}

        assert_game_state(game, game_event, is_completed=False, player1=game_event.player1,
                          player2=game_event.player2, card1=None, card2=None, action="trade", current_player=game_event.player1.id)

        assert_game_cards(game, game_event, card_player_1, card_player_2)

        response1 = client.put(
            "/game/1/trade_card", json={"playerID": game_event.player1.id, "cardID": card_player_1.id})

        assert response1.status_code == 200

        assert_game_state(game, game_event, is_completed=False, player1=game_event.player1,
                          player2=game_event.player2, card1=card_player_1, card2=None, action="trade", current_player=game_event.player2.id)

        assert_game_cards(game, game_event, card_player_1, card_player_2)

        response2 = client.put(
            "/game/1/trade_card", json={"playerID": game_event.player2.id, "cardID": card_player_1.id})

        assert response2.status_code == 400
        assert response2.json() == {"detail": "Player doesn't have that card"}

        assert_game_state(game, game_event, is_completed=False, player1=game_event.player1,
                          player2=game_event.player2, card1=card_player_1, card2=None, action="trade", current_player=game_event.player2.id)

        assert_game_cards(game, game_event, card_player_1, card_player_2)

        response2 = client.put(
            "/game/1/trade_card", json={"playerID": game_event.player2.id, "cardID": 800})

        assert response2.status_code == 400
        assert response2.json() == {"detail": "Player doesn't have that card"}

        assert_game_state(game, game_event, is_completed=False, player1=game_event.player1,
                          player2=game_event.player2, card1=card_player_1, card2=None, action="trade", current_player=game_event.player2.id)

        assert_game_cards(game, game_event, card_player_1, card_player_2)

        response2 = client.put(
            "/game/1/trade_card", json={"playerID": game_event.player2.id, "cardID": card_player_2.id})

        assert response2.status_code == 200

        next_position = (game.players.get(
            id=game_event.player1.id).position+1) % len(game.players)

        assert_game_state(game, game_event, is_completed=True, player1=game_event.player1,
                          player2=game_event.player2, card1=card_player_1, card2=card_player_2, action="draw", current_player=next_position, is_successful=True)

        assert_game_cards(game, game_event, card_player_2, card_player_1)

def test_trade_in_invalid_turn_state(db_game_creation_with_trade_event):
    with db_session:
        game, game_event, cards_player_1, cards_player_2 = get_game_and_cards()
        card_player_1 = cards_player_1[1]
        card_player_2 = cards_player_2[3]

        response1 = client.put(
            "/game/1/trade_card", json={"playerID": game_event.player2.id, "cardID": card_player_2.id})

        assert response1.status_code == 403
        assert response1.json() == {"detail": "Player not has permission to execute this action"}
        
        assert_game_state(game, game_event, is_completed=False, player1=game_event.player1,
                          player2=game_event.player2, card1=None, card2=None, action="trade", current_player=game_event.player1.id)

        assert_game_cards(game, game_event, card_player_1, card_player_2)

        game.current_action = "action"

        response1 = client.put(
            "/game/1/trade_card", json={"playerID": game_event.player1.id, "cardID": card_player_1.id})

        assert response1.status_code == 403
        assert response1.json() == {"detail": "Player not has permission to execute this action"}

        assert_game_state(game, game_event, is_completed=False, player1=game_event.player1,
                            player2=game_event.player2, card1=None, card2=None, action="action", current_player=game_event.player1.id)
        
        assert_game_cards(game, game_event, card_player_1, card_player_2)

        game.current_action = "trade"

        response1 = client.put(
            "/game/1/trade_card", json={"playerID": game_event.player1.id, "cardID": card_player_1.id})
        
        assert response1.status_code == 200

        assert_game_state(game, game_event, is_completed=False, player1=game_event.player1,
                            player2=game_event.player2, card1=card_player_1, card2=None, action="trade", current_player=game_event.player2.id)
        
        assert_game_cards(game, game_event, card_player_1, card_player_2)

        response2 = client.put(
            "/game/1/trade_card", json={"playerID": game_event.player1.id, "cardID": card_player_1.id})
        
        assert response2.status_code == 403
        assert response2.json() == {"detail": "Player not has permission to execute this action"}

        assert_game_state(game, game_event, is_completed=False, player1=game_event.player1,
                            player2=game_event.player2, card1=card_player_1, card2=None, action="trade", current_player=game_event.player2.id)
        
        assert_game_cards(game, game_event, card_player_1, card_player_2)

        response2 = client.put(
            "/game/1/trade_card", json={"playerID": game_event.player2.id, "cardID": card_player_2.id})
        
        assert response2.status_code == 200

        next_position = (game.players.get(
            id=game_event.player1.id).position+1) % len(game.players)
        
        assert_game_state(game, game_event, is_completed=True, player1=game_event.player1,
                            player2=game_event.player2, card1=card_player_1, card2=card_player_2, action="draw", current_player=next_position, is_successful=True)
        
        assert_game_cards(game, game_event, card_player_2, card_player_1)




