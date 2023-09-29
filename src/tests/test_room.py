from main import app
from fastapi.testclient import TestClient
from models import Player, WaitingRoom, db
from pony.orm import db_session
from .util import setup_test_db
import pytest

client=TestClient(app)

# Fixture para configurar la base de datos
@pytest.fixture()
def setup_database():
    global db
    if db is None:
        db = setup_test_db()
    else:
        # Limpiar todas las tablas antes de cada módulo
        db.drop_all_tables(with_all_data=True)
        db.create_tables()
        with db_session:
            WaitingRoom(id=0, room_name="Test_room")
            WaitingRoom(id=1, room_name="Test_room2")
    yield

# Test para la función add_player_to_waiting_room con una room valida
def test_add_player_to_waiting_room_valid(setup_database):
    # Realiza una solicitud POST a la ruta /room/0/players
    response = client.post("/room/0/players", json={"playerName": "Test_player"})

    # Verifica que la respuesta tenga un código de estado 200 (OK)
    assert response.status_code == 200

    # Verifica que la respuesta contenga el ID del jugador
    assert response.json() == {"playerID": 1}

    # Verifica que el jugador se haya agregado correctamente a la sala de espera
    with db_session:
        waiting_room = WaitingRoom.get(id=0)
        player = Player.get(id=1)
        assert player in waiting_room.players

# Test para la función add_player_to_waiting_room con una room invalida
def test_add_player_to_waiting_room_invalid(setup_database):
    # Realiza una solicitud POST a la ruta /room/1/players
    response = client.post("/room/999/players", json={"playerName": "Test_player"})

    # Verifica que la respuesta tenga un código de estado 404 (Not Found)
    assert response.status_code == 404

    # verifica que el usuario no se haya creado
    with db_session:
        player = Player.get(id=1)
        assert player is None


# Test para la funcion añadir muchos jugadores a una sala
def test_add_many_players_to_waiting_room(setup_database):
    # Realiza uchas solicitudes POST a la ruta /room/0/players
    response = client.post("/room/0/players", json={"playerName": "Test_player1"})
    response = client.post("/room/0/players", json={"playerName": "Test_player2"})
    response = client.post("/room/0/players", json={"playerName": "Test_player3"})
    response = client.post("/room/0/players", json={"playerName": "Test_player4"})
    response = client.post("/room/0/players", json={"playerName": "Test_player5"})

    # Verifica que la respuesta tenga un código de estado 200 (OK)
    assert response.status_code == 200

    # Verifica que la respuesta contenga el ID del jugador
    assert response.json() == {"playerID": 5}

    # Verifica que todo los jugadroes se hayan agregado correctamente a la sala de espera
    for i in range(1, 6):
        with db_session:
            waiting_room = WaitingRoom.get(id=0)
            player = Player.get(id=i)
            assert player in waiting_room.players

# Test para la funcion llamar add player sin ningun parametro
def test_add_player_to_waiting_room_bad_request(setup_database):
    # Realiza una solicitud POST a la ruta /room/0/players
    response = client.post("/room/0/players", json={})

    # Verifica que la respuesta tenga un código de estado 422 (Unprocessable Entity)
    assert response.status_code == 422

    # verifica que el usuario no se haya creado
    with db_session:
        player = Player.get(id=1)
        assert player is None

# Test para la funcion añadir jugador sin nombre
def test_add_player_to_waiting_room_no_name(setup_database):
    # Realiza una solicitud POST a la ruta /room/0/players
    response = client.post("/room/0/players", json={"playerName": ""})

    # Verifica que la respuesta tenga un código de estado 400 (Bad Request)
    assert response.status_code == 400

    # verifica que el usuario no se haya creado
    with db_session:
        player = Player.get(id=1)
        assert player is None