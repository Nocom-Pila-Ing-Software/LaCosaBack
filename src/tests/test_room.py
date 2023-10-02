from main import app
from fastapi.testclient import TestClient
from models import WaitingRoom, Player, db
from pony.orm import db_session, select
from schemas.room import RoomCreationRequest, RoomID, PlayerID, RoomCreationResponse
import pytest
from .room_fixtures import db_room_creation, setup_database


client = TestClient(app)


def test_create_room_success(db_room_creation):
    mock_creation_request = RoomCreationRequest(
        roomName="Test Room",
        hostName="Test Host"
    ).model_dump()

    creation_response = RoomCreationResponse(
        roomID=1,
        playerID=1
    ).model_dump()

    response = client.post("/room", json=mock_creation_request)
    data = response.json()

    assert response.status_code == 201
    assert data == creation_response

    with db_session:
        room_record = select(r for r in WaitingRoom if r.id ==
                             int(data["roomID"])).get()

        # Room was created
        assert room_record is not None

        # Host was created
        assert len(room_record.players) == 1

        # Host is host
        player_list = list(room_record.players)
        assert player_list[0].is_host


def test_create_room_duplicate_name(db_room_creation):
    mock_creation_request = RoomCreationRequest(
        roomName="Test Room2",
        hostName="Test Host"
    ).model_dump()

    response = client.post("/room", json=mock_creation_request)
    data = response.json()

    assert response.status_code == 400
    assert data["detail"] == "Room name already exists"

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
