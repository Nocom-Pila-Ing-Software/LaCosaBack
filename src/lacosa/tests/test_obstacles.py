from pony.orm import db_session
from fastapi.testclient import TestClient
from main import app
from .game_fixtures import game_with_obstacle, game_with_obstacle_left_order
from models import Game

client = TestClient(app)


def test_discard_card_when_obstacle(game_with_obstacle):
    data = game_with_obstacle
    game_id = data["game"]["id"]
    card_id = data["cards"][0][0]["id"]
    player_id = data["players"][0]["id"]
    player2_id = data["players"][1]["id"]

    discard_request = {
        "playerID": player_id,
        "cardID": card_id,
    }

    response = client.put(
        f"/game/{game_id}/discard-card", json=discard_request)

    assert response.status_code == 200

    with db_session:
        game = Game.get(id=game_id)
        assert game.current_action == "draw"
        assert game.current_player == player2_id


def test_targets_not_showing_when_obstacle(game_with_obstacle):
    data = game_with_obstacle
    player_id = data["players"][0]["id"]
    card_id = data["cards"][0][0]["id"]

    response = client.get(f"/player/{player_id}/targets/{card_id}")

    assert response.status_code == 200

    response = response.json()
    targets = response["targets"]
    assert len(targets) == 1
    assert targets[0]["name"] == "Player3"
    assert "Player2" not in {target["name"] for target in targets}


def test_play_card_when_obstacle(game_with_obstacle):
    data = game_with_obstacle
    player_id = data["players"][0]["id"]
    player2_id = data["players"][1]["id"]
    card_id = data["cards"][0][0]["id"]
    game_id = data["game"]["id"]
    mock_play_request = {
        "playerID": player_id,
        "targetPlayerID": player2_id,
        "cardID": card_id
    }

    response = client.put(f"/game/{game_id}/play-card", json=mock_play_request)

    assert response.status_code == 403
    assert response.json()["detail"] == "Player can't execute this action"


def test_discard_card_when_obstacle_left_order(game_with_obstacle_left_order):
    data = game_with_obstacle_left_order
    game_id = data["game"]["id"]
    card_id = data["cards"][1][0]["id"]
    player_id = data["players"][1]["id"]
    player2_id = data["players"][0]["id"]

    discard_request = {
        "playerID": player_id,
        "cardID": card_id,
    }

    response = client.put(
        f"/game/{game_id}/discard-card", json=discard_request)

    assert response.status_code == 200

    with db_session:
        game = Game.get(id=game_id)
        assert game.current_action == "draw"
        assert game.current_player == player2_id


def test_targets_not_showing_when_obstacle_left_order(game_with_obstacle_left_order):
    data = game_with_obstacle_left_order
    player_id = data["players"][1]["id"]
    card_id = data["cards"][1][2]["id"]

    response = client.get(f"/player/{player_id}/targets/{card_id}")

    assert response.status_code == 200

    response = response.json()
    targets = response["targets"]
    assert len(targets) == 1
    assert targets[0]["name"] == "Player3"
    assert "Player2" not in {target["name"] for target in targets}


def test_play_card_when_obstacle_left_order(game_with_obstacle_left_order):
    data = game_with_obstacle_left_order
    player_id = data["players"][1]["id"]
    player2_id = data["players"][0]["id"]
    card_id = data["cards"][1][2]["id"]
    game_id = data["game"]["id"]
    mock_play_request = {
        "playerID": player_id,
        "targetPlayerID": player2_id,
        "cardID": card_id
    }

    response = client.put(f"/game/{game_id}/play-card", json=mock_play_request)

    assert response.status_code == 403
    assert response.json()["detail"] == "Player can't execute this action"
