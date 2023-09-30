from main import app
from fastapi.testclient import TestClient
from models import Player, WaitingRoom, db
from pony.orm import db_session
import pytest

client=TestClient(app)

# Fixture para configurar la base de datos
@pytest.fixture()
def setup_database():
    global db
    db.drop_all_tables(with_all_data=True)
    db.create_tables()
    with db_session:
        WaitingRoom(id=0, room_name="Test_room")
        WaitingRoom(id=1, room_name="Test_room2")
    yield

# Test para la función add_player_to_waiting_room con una room valida
def test_add_player_to_waiting_room_valid(setup_database):
    response = client.post("/room/0/players", json={"playerName": "Test_player"})

    assert response.status_code == 200
    assert response.json() == {"playerID": 1}

    with db_session:
        waiting_room = WaitingRoom.get(id=0)
        player = Player.get(id=1)
        assert player in waiting_room.players

# Test para la función add_player_to_waiting_room con una room invalida
def test_add_player_to_waiting_room_invalid(setup_database):
    response = client.post("/room/999/players", json={"playerName": "Test_player"})

    assert response.status_code == 404

    with db_session:
        player = Player.get(id=1)
        assert player is None


# Test para la funcion añadir muchos jugadores a una sala
def test_add_many_players_to_waiting_room(setup_database):
    response = client.post("/room/0/players", json={"playerName": "Test_player1"})
    response = client.post("/room/0/players", json={"playerName": "Test_player2"})
    response = client.post("/room/0/players", json={"playerName": "Test_player3"})
    response = client.post("/room/0/players", json={"playerName": "Test_player4"})
    response = client.post("/room/0/players", json={"playerName": "Test_player5"})

    assert response.status_code == 200
    assert response.json() == {"playerID": 5}

    for i in range(1, 6):
        with db_session:
            waiting_room = WaitingRoom.get(id=0)
            player = Player.get(id=i)
            assert player in waiting_room.players

# Test para la funcion llamar add player sin ningun parametro
def test_add_player_to_waiting_room_bad_request(setup_database):
    response = client.post("/room/0/players", json={})

    assert response.status_code == 422

    with db_session:
        player = Player.get(id=1)
        assert player is None

# Test para la funcion añadir jugador sin nombre
def test_add_player_to_waiting_room_no_name(setup_database):
    response = client.post("/room/0/players", json={"playerName": ""})

    assert response.status_code == 400

    with db_session:
        player = Player.get(id=1)
        assert player is None