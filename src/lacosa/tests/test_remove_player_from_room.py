from main import app
from fastapi.testclient import TestClient
from pony.orm import db_session
from lacosa.game.schemas import GameCreationRequest
from models import WaitingRoom
from .room_fixtures import db_room_creation_with_players, db_room_creation

client = TestClient(app)


def test_valid_request(db_room_creation_with_players):
    response = client.request("DELETE", "/room/0/player", json={"playerID": 2})
    assert response.status_code == 200
    with db_session:
        room = WaitingRoom.get(id=0)
        assert room.players.count() == 2
        assert room.players.filter(lambda p: p.id == 2).first() is None


def test_invalid_room_id(db_room_creation_with_players):
    response = client.request(
        "DELETE", "/room/666/player", json={"playerID": 2})
    assert response.status_code == 404


def test_invalid_player_id(db_room_creation):
    response = client.request(
        "DELETE", "/room/0/player", json={"playerID": 666})
    assert response.status_code == 400


def test_remove_player_when_game_started(db_room_creation_with_players):
    mock_creation_request = GameCreationRequest(roomID=0,).model_dump()
    response = client.post("/game", json=mock_creation_request)

    response = client.request(
        "DELETE", "/room/0/player", json={"playerID": 2})

    assert response.status_code == 403


def test_remove_host(db_room_creation_with_players):
    response = client.request(
        "DELETE", "/room/0/player", json={"playerID": 1})
    assert response.status_code == 200

    with db_session:
        assert WaitingRoom.get(id=0) is None
