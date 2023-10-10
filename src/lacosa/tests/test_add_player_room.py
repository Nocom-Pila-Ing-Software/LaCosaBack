from main import app
from fastapi.testclient import TestClient
from models import WaitingRoom, Player
from pony.orm import db_session
from lacosa.room.schemas import RoomCreationRequest, RoomCreationResponse
from .room_fixtures import db_room_creation_with_players, db_room_creation
from .game_fixtures import  db_game_creation_without_cards

client = TestClient(app)


# Test para la función add_player_to_waiting_room con una room valida
def test_add_player_to_waiting_room_valid(db_room_creation):
    response = client.post("/room/0/players", json={"playerName": "Test_player2"})

    assert response.status_code == 200
    assert response.json() == {"playerID": 2}

    with db_session:
        waiting_room = WaitingRoom.get(id=0)
        player = Player.get(id=2)
        assert player in waiting_room.players

# Test para la función add_player_to_waiting_room con una room invalida
def test_add_player_to_waiting_room_invalid(db_room_creation):
    response = client.post("/room/999/players", json={"playerName": "Test_player2"})

    assert response.status_code == 404

    with db_session:
        player = Player.get(id=2)
        assert player is None


# Test para la funcion añadir muchos jugadores a una sala
def test_add_many_players_to_waiting_room(db_room_creation):
    response = client.post("/room/0/players", json={"playerName": "Test_player2"})
    response = client.post("/room/0/players", json={"playerName": "Test_player3"})
    response = client.post("/room/0/players", json={"playerName": "Test_player4"})
    response = client.post("/room/0/players", json={"playerName": "Test_player5"})
    response = client.post("/room/0/players", json={"playerName": "Test_player6"})

    assert response.status_code == 200
    assert response.json() == {"playerID": 6}

    for i in range(2, 7):
        with db_session:
            waiting_room = WaitingRoom.get(id=0)
            player = Player.get(id=i)
            assert player in waiting_room.players

# Test para la funcion llamar add player sin ningun parametro
def test_add_player_to_waiting_room_bad_request(db_room_creation):
    response = client.post("/room/0/players", json={})

    assert response.status_code == 422

    with db_session:
        player = Player.get(id=2)
        assert player is None

# Test para la funcion añadir jugador sin nombre
def test_add_player_to_waiting_room_no_name(db_room_creation):
    response = client.post("/room/0/players", json={"playerName": ""})

    assert response.status_code == 400

    with db_session:
        player = Player.get(id=2)
        assert player is None

def test_add_player_to_waiting_room_already_exists(db_room_creation_with_players):
    response = client.post("/room/0/players", json={"playerName": "Test_player"})

    assert response.status_code == 400

    with db_session:
        player = Player.get(id=1)
        assert player is not None
        assert player.username == "Test_player"   

def test_add_player_to_waiting_room_game_started(db_game_creation_without_cards):
    response = client.post("/room/0/players", json={"playerName": "Test_player"})

    assert response.status_code == 400

    with db_session:
        player = Player.get(id=2)
        assert player is None