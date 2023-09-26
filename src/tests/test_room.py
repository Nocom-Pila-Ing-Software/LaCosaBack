from main import app
from fastapi.testclient import TestClient
from models import Player, WaitingRoom
from pony.orm import db_session
from schemas.room import RoomID, PlayerID
from .util import setup_test_db
import pytest

client=TestClient(app)

def setup_database():
    with db_session:
        room = WaitingRoom(id=0, room_name="Test room")
        room.players.create(username="Player1")

@pytest.fixture(scope="module")
def test_client():
    setup_test_db()
    setup_database()

# Test para la función add_player_to_waiting_room con un jugador válido
def test_add_player_to_waiting_room_valid(test_client):
    # Envía una solicitud POST para agregar un jugador válido
    response = client.post("/room/0/player/1")

    # Verifica que la respuesta tenga un código de estado 200 (OK)
    assert response.status_code == 200

    # Verifica que la respuesta contenga el ID del jugador
    player_id = response.json()
    assert isinstance(player_id, PlayerID)
    assert player_id.playerID == 1

    # Verifica que el jugador se haya agregado correctamente a la sala de espera
    with db_session:
        waiting_room = WaitingRoom.get(id=0)
        player = Player.get(id=1)
        assert player in waiting_room.players