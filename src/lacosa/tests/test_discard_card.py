from main import app
from fastapi.testclient import TestClient
from pony.orm import db_session
from models import Game, Player, Card
# from lacosa.schemas import PlayerID, GameID, CardInfo
# from lacosa.game.schemas import GameCreationRequest, PublicPlayerInfo, GameStatus, PlayCardRequest
from .game_fixtures import discard_card_game_creation

client = TestClient(app)


def test_discard_card_success(discard_card_game_creation):
    # Mock data
    room_id = discard_card_game_creation["room"]["id"]
    card_id = discard_card_game_creation["cards"][0][0]["id"]
    player_id = discard_card_game_creation["players"][0]["id"]

    discard_request = {
        "playerID": player_id,
        "cardID": card_id,
    }

    response = client.put(
        f"/game/{room_id}/discard-card", json=discard_request)

    assert response.status_code == 200
    assert response.json() == None

    with db_session:
        game = Game.get(id=room_id)
        player = Player.get(id=player_id)
        card = Card.get(id=card_id)
        assert card not in player.cards
        assert card in game.cards


def test_discard_card_invalid_player(discard_card_game_creation):
    # Mock data with an invalid player
    room_id = discard_card_game_creation["room"]["id"]
    discard_request = {
        "playerID": 666,
        "cardID": discard_card_game_creation["cards"][0][0]["id"],
    }

    response = client.put(
        f"/game/{room_id}/discard-card", json=discard_request)

    assert response.status_code == 400


def test_discard_card_invalid_card(discard_card_game_creation):
    room_id = discard_card_game_creation["room"]["id"]
    # Mock data with an invalid card
    discard_request = {
        "playerID": discard_card_game_creation["players"][0]["id"],
        "cardID": 666,
    }

    response = client.put(
        f"/game/{room_id}/discard-card", json=discard_request)

    assert response.status_code == 400


def test_discard_card_invalid_player_turn(discard_card_game_creation):
    room_id = discard_card_game_creation["room"]["id"]
    # Mock data with a player who is not in turn
    discard_request = {
        "playerID": discard_card_game_creation["players"][1]["id"],
        "cardID": discard_card_game_creation["cards"][1][0]["id"],
    }

    # Implement a method to change the player's turn in the game here if needed

    response = client.put(
        f"/game/{room_id}/discard-card", json=discard_request)

    assert response.status_code == 403
    assert response.json() == {'detail': "Can't discard card, it's not your turn"}
